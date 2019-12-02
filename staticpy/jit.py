import importlib
import inspect
import os
import sys

from .template import CppTemplate
from .bind import PyBindFunction, PyBindFunctionGroup
from .common.options import get_option
from .compiler import Compiler
from .translator import BaseTranslator
from .session import new_session
from .util.string import get_target_filepath
from .lang.common import get_block_or_create
from .lang import (
    statement as S,
    expression as E,
    macro as M,
    block as B,
    type as T,
    variable as V,
)


class JitObject:
    def __init__(self, name, obj):
        self.name = name
        self.obj = obj
        self.source = self._get_source(obj)
        self._signatures = []
        self._compiled = False
        self._compiled_obj = None
        self._source_path, self._target_path = self._get_paths(obj)

    def compile(self):
        sess = new_session()
        self._translate(sess)
        self._bind(sess)
        self._compile(sess)

    def load(self):
        module_name = self.name
        if module_name in sys.modules:
            del sys.modules[module_name]
        sys.path.insert(0, os.path.dirname(self._target_path))
        try:
            module = importlib.import_module(module_name)
            self._compiled_obj = getattr(module, self.name)
        finally:
            del sys.path[0]

    def _translate(self, sess):
        pass

    @staticmethod
    def _get_source(obj):
        if isinstance(obj, str):
            with open(obj, "r") as f:
                return f.read()
        else:
            return inspect.getsource(obj)

    @staticmethod
    def _get_paths(obj):
        if inspect.ismodule(obj) or inspect.isfunction(obj) or inspect.isclass(obj):
            sourcepath = inspect.getsourcefile(obj)
            path = os.path.dirname(sourcepath)
            name = obj.__name__
        else:
            sourcepath = obj
            path = os.path.dirname(sourcepath)
            name = os.path.basename(obj).split(".")[0]
        sourcepath = os.path.abspath(sourcepath)
        targetpath = os.path.abspath(get_target_filepath(path, name))
        return sourcepath, targetpath

    def _wrap_function(self, name, inputs, output, block):
        doc = block.doc
        wrapped_inputs = [(T.ReferenceType(t) if isinstance(t, T.ArrayType) else t, n) for (t, n) in inputs]
        funcs = [B.Function(name, wrapped_inputs, output, block.statements)]
        # if any, wrap the array types
        if any(isinstance(type, T.ArrayType) for type, name in inputs):
            wrapped_inputs = []
            params = []
            block = B.EmptyBlock()
            auto_t = T.OtherType(V.Name("auto"))
            with block:
                for t, n in inputs:
                    if isinstance(t, T.ArrayType):
                        buffer_t = T.OtherType(E.ScopeAnalysis(V.Name("py"), V.Name("buffer")))
                        wrapped_inputs.append((buffer_t, n))
                        v_in = V.variable(n, buffer_t)
                        v_out = V.variable("_" + n, t)
                        buffer_info = V.variable(f"buffer_info_{n}", auto_t)
                        S.declare(buffer_info, E.CallFunction(E.GetAttr(v_in, "request"), ()))
                        S.declare(v_out, E.CallFunction(t.cname(), (buffer_info, )))
                        params.append(v_out)
                    else:
                        wrapped_inputs.append((t, n))
                        params.append(V.variable(n, t))
                S.returns(E.CallFunction(name, tuple(params)))
            block = B.Function(name, wrapped_inputs, output, block.statements, doc)
            m = M.IfDefMacro("PYBIND")
            m.add_statement(S.BlockStatement(block))
            funcs.append(m)
            inputs = wrapped_inputs
        else:
            inputs = [(t.wrapped(), n) for t, n in inputs]
        return funcs, inputs

    def _bind(self, sess):
        with sess:
            with get_block_or_create("header"):
                M.defineM("PYBIND")
        funcs = []
        for sig in self._signatures:
            funcs.append(PyBindFunction(**sig))
        PyBindFunctionGroup(self.name, funcs).setup(sess)

    def _compile(self, sess):
        compiler = Compiler()
        compiler.add_template(".cpp", CppTemplate())
        compiler.run(sess, os.path.dirname(self._target_path), libname=self.name)

    def _need_update(self):
        if not os.path.exists(self._target_path):
            return True
        target_mtime = os.path.getmtime(self._target_path)
        source_mtime = os.path.getmtime(self._source_path)
        return source_mtime > target_mtime


class JitModule(JitObject):
    def _translate(self, sess):
        translator = BaseTranslator(session=sess)
        module_block = translator.translate(self.source)
        sess.blocks['global'] = module_block
        for stmt in module_block.statements:
            if isinstance(stmt, S.BlockStatement) and isinstance(stmt.block, B.Function):
                block = stmt.block
                funcs, inputs = self._wrap_function(block.name, block.inputs, block.output, block)
                for func in funcs[1:]:
                    module_block.add_statement(S.BlockStatement(func))
                self._signatures.append({
                    "name": block.name,
                    "inputs": inputs,
                    "output": block.output,
                    "doc": block.doc,
                })


class JitFunction(JitObject):
    def __init__(self, func, env={}):
        super().__init__(func.__name__, func)
        self.env = env.copy()
        self.env[func.__name__] = V.Name(func.__name__)

    def __call__(self, *args):
        if not self._compiled:
            if get_option("force_compile", False) or self._need_update():
                self.compile()
            self.load()
            self._compiled = True
            self.__doc__ = self._compiled_obj.__doc__
        return self._compiled_obj(*args)

    def _translate(self, sess):
        with sess:
            global_block = get_block_or_create('global')
        translator = BaseTranslator(self.env, session=sess)
        block = translator.translate(self.source).statements[0].block
        funcs, inputs = self._wrap_function(self.name, block.inputs, block.output, block)
        for func in funcs:
            global_block.add_statement(S.BlockStatement(func))
        self._signatures.append({
            "name": self.name,
            "inputs": inputs,
            "output": block.output,
            "doc": block.doc,
        })


def jit(obj):
    if inspect.isfunction(obj):
        frame = inspect.currentframe().f_back
        env = frame.f_globals
        return JitFunction(obj, env)
    elif inspect.ismodule(obj) or isinstance(obj, str):
        return JitModule(obj)

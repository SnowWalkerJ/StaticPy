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


class JitFunction:
    def __init__(self, func):
        self.name = func.__name__
        self.funcs = [func]
        self._compiled = False
        self._compiled_func = None
        self._signatures = []
        self._target_path = os.path.dirname(inspect.getabsfile(self.funcs[0]))

    def overload(self, func):
        self.funcs.append(func)

    def compile(self):
        sess = new_session()
        self._translate(sess)
        self._bind(sess)
        self._compile(sess)

    def load(self):
        module_name = "lib" + self.name
        if module_name in sys.modules:
            del sys.modules[module_name]
        sys.path.insert(0, self._target_path)
        module = importlib.import_module(module_name)
        self._compiled_func = getattr(module, self.name)

    def __call__(self, *args):
        if not self._compiled:
            if get_option("force_compile", False) or self._need_update():
                self.compile()
            self.load()
            self._compiled = True
        return self._compiled_func(*args)

    def _translate(self, sess):
        with sess:
            global_block = get_block_or_create('global')
        for func in self.funcs:
            name = func.__name__
            translator = BaseTranslator(session=sess)
            block = translator.translate(inspect.getsource(func)).statements[0].block
            funcs, inputs = self._wrap_function(name, block.inputs, block.output, block)
            for func in funcs:
                global_block.add_statement(S.BlockStatement(func))
            self._signatures.append({
                "name": name,
                "inputs": inputs,
                "output": block.output,
            })

    def _wrap_function(self, name, inputs, output, block):
        wrapped_inputs = [(T.ReferenceType(t) if isinstance(t, T.ArrayType) else t, n) for (t, n) in inputs]
        funcs = [B.Function(name, wrapped_inputs, output, block.statements)]
        # if any, wrap the array types
        if any(isinstance(type, T.ArrayType) for type, name in inputs):
            # TODO: check shape and itemsize
            # TODO: shorten this function
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
            block = B.Function(name, wrapped_inputs, output, block.statements)
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
        PyBindFunctionGroup("lib" + self.name, funcs).setup(sess)

    def _compile(self, sess):
        compiler = Compiler()
        compiler.add_template(".cpp", CppTemplate())
        compiler.run(sess, self._target_path, libname="lib" + self.name)

    def _need_update(self):
        targetfile = get_target_filepath(self._target_path, libname="lib" + self.name)
        if not os.path.exists(targetfile):
            return True
        target_mtime = os.path.getmtime(targetfile)
        for func in self.funcs:
            sourcefile = inspect.getabsfile(func)
            if os.path.getmtime(sourcefile) > target_mtime:
                return True
        return False


def jit(obj):
    if inspect.isfunction(obj):
        return JitFunction(obj)

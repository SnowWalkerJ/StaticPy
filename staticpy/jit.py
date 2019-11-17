import importlib
import inspect
import os
import sys

from .template import CppTemplate
from .bind import PyBindFunction, PyBindFunctionGroup
from .common.options import get_option
from .compiler import Compiler
from .vm import FunctionVM
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


class Function:
    def __init__(self, func):
        self.name = func.__name__
        self.funcs = [func]

    def overload(self, func):
        raise NotImplementedError

    def __call__(self, *args):
        pass


class JitFunction(Function):
    def __init__(self, func):
        super().__init__(func)
        self._compiled = False
        self._compiled_func = None
        self._signatures = []
        self._target_path = os.path.dirname(inspect.getabsfile(self.funcs[0]))

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
            vm = FunctionVM(func, session=sess)
            block = vm.run()
            funcs, inputs = self._wrap_function(name, vm.inputs, vm.output, block)
            for func in funcs:
                global_block.add_statement(S.BlockStatement(func))
            self._signatures.append({
                "name": name,
                "inputs": inputs,
                "output": vm.output,
            })

    def _wrap_function(self, name, inputs, output, block):
        funcs = [B.Function(name, inputs, output, block.statements)]
        # if any, wrap the array types
        if any(isinstance(type, T.ArrayType) for type, name in inputs):
            wrapped_inputs = []
            params = []
            block = B.EmptyBlock()
            with block:
                buffer_info_t = T.OtherType(E.ScopeAnalysis(V.Name("py"), V.Name("buffer_info")))
                bi = V.Variable("bi", buffer_info_t)
                S.declare(bi)
                for t, n in inputs:
                    if isinstance(t, T.ArrayType):
                        buffer_t = T.OtherType(E.ScopeAnalysis(V.Name("py"), V.Name("buffer")))
                        wrapped_inputs.append((buffer_t, n))
                        v_in = V.Variable(n, buffer_t)
                        if isinstance(t, T.SimpleArrayType):
                            v_out = V.Variable("_" + n, t.wrapped())
                            S.assign(bi, E.CallFunction(E.GetAttr(v_in, "request"), ()))
                            ptr = E.StaticCast(E.GetAttr(bi, "ptr"), T.PointerType(t.base))
                            S.declare(v_out, ptr)
                        elif isinstance(t, T.ComplexArrayType):
                            v_out = V.Variable("_" + n, t)
                            S.assign(bi, E.CallFunction(E.GetAttr(v_in, "request"), ()))
                            ptr = E.StaticCast(E.GetAttr(bi, "ptr"), T.PointerType(t.base))
                            shape = E.GetAttr(bi, "shape")
                            args = [ptr]
                            for index in range(t.dim):
                                args.append(E.GetItem(shape, index))
                            S.declare(v_out, E.CallFunction(t.cname(), tuple(args)))
                        params.append(v_out)
                    else:
                        wrapped_inputs.append((t, n))
                        params.append(V.Variable(n, t))
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

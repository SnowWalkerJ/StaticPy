import importlib
import inspect
import os
import sys

from .template import CppTemplate
from .bind import PyBindFunction, PyBindFunctionGroup
from .compiler import Compiler
from .vm import FunctionVM
from .session import new_session
from .lang.common import get_block_or_create
from .lang import statement as S, macro as M


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
        sys.path.insert(0, self._target_path)
        module = importlib.import_module("lib" + self.name)
        self._compiled_func = getattr(module, self.name)

    def __call__(self, *args):
        if not self._compiled:
            self.compile()
            self.load()
            self._compiled = True
        return self._compiled_func(*args)

    def _translate(self, sess):
        with sess:
            global_block = get_block_or_create('global')
        for func in self.funcs:
            vm = FunctionVM(func, session=sess)
            block = vm.run()
            global_block.add_statement(S.BlockStatement(block))
            self._signatures.append({
                "name": func.__name__,
                "inputs": vm.inputs,
                "output": vm.output,
            })

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


def jit(obj):
    if inspect.isfunction(obj):
        return JitFunction(obj)

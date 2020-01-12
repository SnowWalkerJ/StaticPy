import importlib
import inspect
import os
import sys

from .template import CppTemplate
from .bind import PyBindFunction, PyBindModule
from .common.options import get_option
from .common.phase import TwoPhaseFunction
from .compiler import Compiler
from .translator import BaseTranslator
from .session import new_session, get_session
from .common.string import get_target_filepath
from .lang.common import get_block_or_create
from .lang import (
    statement as S,
    expression as E,
    macro as M,
    block as B,
    type as T,
    variable as V,
)


class JitObject(TwoPhaseFunction):
    def __init__(self, name, obj, env={}):
        self.name = name or obj.__name__
        self.obj = obj
        self.env = env.copy()
        self.env[self.name] = V.Name(self.name)
        self.source = self._get_source(obj)
        self._signatures = []
        self._compiled = False
        self._compiled_obj = None
        self._source_path, self._target_path = self._get_paths(obj)

    def compile(self):
        sess = new_session()
        block = self._translate(sess)
        self._assemble(sess, block)
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

    def building(self, *args):
        get_session().add_definition(self)
        return E.CallFunction(self.name, args)

    def normal(self, *args):
        if not self._compiled:
            if get_option("force_compile", False) or self._need_update():
                self.compile()
            self.load()
            self._compiled = True
            self.__doc__ = self._compiled_obj.__doc__
        return self._compiled_obj(*args)

    def _translate(self, sess):
        translator = BaseTranslator(self.env, session=sess)
        return translator.translate(self.source)

    def _assemble(self, sess, block):
        sess.blocks["main"] = block
        sess.finalize()

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

    def _bind(self, sess):
        with sess:
            with get_block_or_create("header"):
                M.defineM("PYBIND")
            block = get_block_or_create("main")
        PyBindModule(self.name, block).setup(sess)

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


def jit(obj):
    frame = inspect.currentframe().f_back
    env = dict(__builtins__).copy()
    env.update(frame.f_globals)
    env.update(frame.f_locals)
    return JitObject(obj.__name__, obj, env)

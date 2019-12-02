import importlib
import inspect
import os
import sys

from .template import CppTemplate
from .bind import PyBindFunction, PyBindModule
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

    def _bind(self, sess):
        with sess:
            with get_block_or_create("header"):
                M.defineM("PYBIND")
            block = get_block_or_create("global")
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


class JitModule(JitObject):
    def _translate(self, sess):
        translator = BaseTranslator(session=sess)
        module_block = translator.translate(self.source)
        sess.blocks['global'] = module_block


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
        translator = BaseTranslator(self.env, session=sess)
        module_block = translator.translate(self.source)
        sess.blocks['global'] = module_block


def jit(obj):
    if inspect.isfunction(obj):
        frame = inspect.currentframe().f_back
        env = frame.f_globals
        return JitFunction(obj, env)

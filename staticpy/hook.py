from importlib.abc import MetaPathFinder, Loader
from importlib.machinery import ModuleSpec
from importlib.util import spec_from_file_location, module_from_spec
import inspect
import os
import sys

from .common.options import get_option
from .jit import JitModule


class StaticPyFinder(MetaPathFinder):
    def find_spec(self, fullname, path, target=None):
        name = fullname.split(".")[-1] + ".py"
        paths = path or sys.path
        for path in paths:
            filename = os.path.join(path, name)
            if os.path.exists(filename):
                with open(filename) as f:
                    line = f.readline()
                    if line[:2] == "#!":
                        line = f.readline()
                if line == "# @staticpy\n":
                    return ModuleSpec(fullname, StaticPyLoader(), origin=filename)


class StaticPyLoader(Loader):
    def create_module(self, spec):
        name = spec.name.split(".")[-1]
        jit = JitModule(name, spec.origin, dict(inspect.getmembers(__builtins__)))
        if get_option("force_compile", False) or jit._need_update():
            jit.compile()
        self.wrapped_spec = spec_from_file_location(name, jit._target_path)
        module = module_from_spec(self.wrapped_spec)
        return module

    def exec_module(self, module):
        self.wrapped_spec.loader.exec_module(module)


def install_hook():
    finder = StaticPyFinder()
    sys.meta_path.insert(0, finder)
    return finder


def remove_hook():
    sys.meta_path.remove(finder)


finder = install_hook()

import abc
from contextlib import contextmanager
import inspect
import typing

from ..lang.common.func import get_block_or_create
from ..lang import expression as E, variable as V, macro as M

__building = 0


def is_building():
    return __building


@contextmanager
def set_building():
    global __building
    __building += 1
    yield
    __building -= 1


class TwoPhaseFunction(abc.ABC):
    def __call__(self, *args, **kwargs):
        if is_building():
            return self.building(*args, **kwargs)
        else:
            return self.normal(*args, **kwargs)

    @abc.abstractmethod
    def normal(self, *args, **kwargs):
        pass

    @abc.abstractmethod
    def building(self, *args, **kwargs):
        pass


class LibFunction(TwoPhaseFunction):
    def __init__(self, header, pyfunction, function, namespace=None):
        self.header = header
        self.function = function
        self.pyfunction = pyfunction
        self.namespace = namespace
        if not (hasattr(function, "__call__") or isinstance(function, str)):
            raise TypeError(f"unknown type {type(self.function)}")

    def normal(self, *args, **kwargs):
        return self.pyfunction(*args, **kwargs)

    def building(self, *args, **kwargs):
        with get_block_or_create('header'):
            M.include(self.header)
        if hasattr(self.function, "__call__"):
            return self.function(*args, **kwargs)
        elif isinstance(self.function, str):
            function = E.ScopeAnalysis(self.namespace, self.function) if self.namespace else V.Name(self.function)
            if kwargs:
                raise ValueError("kwargs is invalid for cpp call")
            return E.CallFunction(function, args)


class LibObject(LibFunction):
    def building(self):
        with get_block_or_create('header'):
            M.include(self.header)
        return E.ScopeAnalysis(self.namespace, self.function) if self.namespace else V.Name(self.function)

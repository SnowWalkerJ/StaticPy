import abc
from contextlib import contextmanager
import inspect
import typing

from ..lang.common.func import get_session
from ..lang import expression as E, variable as V, macro as M

__building = 0


def is_building():
    return __building


@contextmanager
def set_building():
    global __building
    __building += 1
    try:
        yield
    finally:
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
        self.function = V.Name(function) if isinstance(function, str) else function
        self.pyfunction = pyfunction
        self.namespace = namespace
        if not (hasattr(function, "__call__") or isinstance(function, str)):
            raise TypeError(f"unknown type {type(self.function)}")

    def normal(self, *args, **kwargs):
        return self.pyfunction(*args, **kwargs)

    def building(self, *args, **kwargs):
        get_session().add_include(self.header)
        if not isinstance(self.function, V.Value):
            return self.function(*args, **kwargs)
        else:
            function = E.ScopeAnalysis(self.namespace, self.function) if self.namespace else self.function
            if kwargs:
                raise ValueError("kwargs is invalid for cpp call")
            return E.CallFunction(function, args)

    def __getitem__(self, *args):
        if not callable(self.function):
            function = E.TemplateInstantiate(self.function, args)
            return LibFunction(self.header, self.pyfunction, function, self.namespace)
        else:
            raise NotImplementedError


class LibObject(LibFunction):
    def building(self):
        get_session().add_include(self.header)
        return E.ScopeAnalysis(self.namespace, self.function) if self.namespace else V.Name(self.function)


class JumpHint(TwoPhaseFunction):
    def __init__(self, name):
        super().__init__()
        self.name = name

    def normal(self, condition):
        return condition

    def building(self, condition):
        return E.CallFunction(V.Name(self.name), (condition, ))


likely = JumpHint("_likely")
unlikely = JumpHint("_unlikely")

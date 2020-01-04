from ..common.phase import is_building
from ..lang import expression as E, variable as V, macro as M
from ..lang.common.func import get_session


class ExternalFunction:
    def __init__(self, name, source=None, namespace=None):
        self.name = V.Name(name) if namespace is None else E.ScopeAnalysis(namespace, name)
        self.source = source

    def __call__(self, *args):
        if not is_building():
            raise NotImplementedError("C++ external objects not accessible in Python")
        if self.source is not None:
            get_session().add_include(self.source)
        return E.CallFunction(self.name, args)

    def __getitem__(self, *args):
        def f(*f_args):
            if not is_building():
                raise NotImplementedError("C++ external objects not accessible in Python")
            if self.source is not None:
                get_session().add_include(self.source)
            func = E.TemplateInstantiate(self.name, args)
            return E.CallFunction(func, f_args)
        return f

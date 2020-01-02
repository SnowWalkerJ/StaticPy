from ..common.phase import is_building
from ..lang import expression as E, variable as V, macro as M
from ..lang.common.func import get_block_or_create


class ExternalFunction:
    def __init__(self, name, source=None, namespace=None, is_template=False):
        self.name = V.Name(name) if namespace is None else E.ScopeAnalysis(namespace, name)
        self.source = source
        self.is_template = is_template

    def __call__(self, *args):
        if not is_building():
            raise NotImplementedError("C++ external objects not accessible in Python")
        if self.source is not None:
            with get_block_or_create('header'):
                M.include(self.source)
        if self.is_template:
            def f(*f_args):
                func = E.TemplateInstantiate(self.name, args)
                return E.CallFunction(func, f_args)
            return f
        else:
            return E.CallFunction(self.name, args)

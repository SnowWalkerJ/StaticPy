# TODO: list and dict
from types import MethodType

from .base import TypeBase
from ..variable import Name


class DerivedType(TypeBase):
    pass


class OtherType(DerivedType):
    def __init__(self, alias):
        self.real_type = alias

    def cname(self):
        return str(self.real_type)

    def prefix(self):
        return ""

    def suffix(self):
        return ""


class ArrayType(DerivedType):
    def __init__(self, base, shape, is_continuous):
        self.base = base
        self.shape = shape
        self.dim = len(shape)
        self.itemsize = base.size
        self.is_continuous = is_continuous

    def instantiate(self):
        from .. import variable as V
        return V.ArrayVariable

    def cname(self):
        from .. import expression as E, variable as V
        return E.TemplateInstantiate(V.Name("Array"), (self.base, len(self.shape)))

    def prefix(self):
        return ""

    def suffix(self):
        return ""

    def wrapped(self):
        from .. import expression as E, variable as V
        clas = E.ScopeAnalysis(V.Name("py"), V.Name("buffer"))
        return OtherType(clas)


AutoType = OtherType(Name("auto"))

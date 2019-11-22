# TODO: list and dict
from types import MethodType

from .base import TypeBase


class DerivedType(TypeBase):
    pass


class PointerType(DerivedType):
    def __init__(self, base):
        self.base = base

    def cname(self):
        return self.base.cname()

    def prefix(self):
        return "*"

    def suffix(self):
        return ""

    def declare(self, name, init=None):
        if init is None:
            return f"{self}{name} = nullptr;"
        else:
            return f"{self}{name} = {init};"


class ReferenceType(DerivedType):
    def __init__(self, base):
        self.base = base

    def cname(self):
        return str(self.base.cname()) + "&"

    def prefix(self):
        return ""

    def suffix(self):
        return ""

    def declare(self, name, init=None):
        if init is None:
            raise ValueError("Can't declare a reference without target")
        else:
            return f"{self}{name} = {init};"


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
    def __init__(self, base, shape):
        self.base = base
        self.shape = shape
        self.dim = len(shape)
        self.itemsize = base.size

    def instantiate(self, variable):
        # TODO: instantiate should return a class
        from .. import expression as E
        variable._shape = self.shape
        variable.shape = [s if isinstance(s, int) else E.GetItem(E.GetAttr(variable, "shape"), i)
                          for i, s in enumerate(self.shape)]
        variable.itemsize = self.itemsize
        variable.dim = self.dim
        variable.__len__ = MethodType(self.len, variable)
        variable.__getitem__ = MethodType(self.getitem, variable)

    @staticmethod
    def len(self):
        return self.shape[0]

    def cname(self):
        from .. import expression as E, variable as V
        return E.TemplateInstantiate(V.Name("Array"), (self.base, len(self.shape)))

    def prefix(self):
        return ""

    def suffix(self):
        return ""

    @staticmethod
    def getitem(self, indices):
        from .. import expression as E
        indices = [x.value if isinstance(x, E.Const) else x for x in indices]
        return E.CallFunction(E.GetAttr(self, "getData"), indices)

    def wrapped(self):
        from .. import expression as E, variable as V
        clas = E.ScopeAnalysis(V.Name("py"), V.Name("buffer"))
        return OtherType(clas)


def make_array_type(base, shape):
    return ArrayType(base, shape)

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
        return f"{self}{name} = nullptr;"


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
        from .. import expression as E
        variable._shape = self.shape
        variable.shape = [s if isinstance(s, int) else E.GetItem(E.GetAttr(variable, "shape"), i)
                          for i, s in enumerate(self.shape)]
        variable.itemsize = self.itemsize
        variable.dim = self.dim
        variable.__len__ = MethodType(self.len, variable)

    @staticmethod
    def len(self):
        return self.shape[0]


class ComplexArrayType(ArrayType):
    def cname(self):
        from .. import expression as E, variable as V
        return E.TemplateInstantiate(V.Name("Array"), (self.base, len(self.shape)))

    def prefix(self):
        return ""

    def suffix(self):
        return ""

    def instantiate(self, variable):
        super().instantiate(variable)
        variable.__getitem__ = MethodType(self.getitem, variable)

    @staticmethod
    def getitem(self, indices):
        if all(isinstance(x, int) for x in self._shape[1:]):
            # if shape is given, calculate the index in Python
            from .. import expression as E
            index = E.Const(0)
            stride = E.Const(1)
            for i, s in reversed(list(zip(indices, self._shape[1:]))):
                index = index + E.cast_value_to_expression(i) * stride
                stride = stride * s
            return E.GetItem(self, index)
        else:
            # call method from c++
            from .. import expression as E
            return E.CallFunction(E.GetAttr(self, "getData"), indices)

    def wrapped(self):
        from .. import expression as E, variable as V
        clas_template = E.ScopeAnalysis(V.Name("py"), V.Name("buffer_t"))
        clas = E.TemplateInstantiate(clas_template, self.base)
        return OtherType(clas)


class SimpleArrayType(ArrayType):
    def cname(self):
        return self.base.cname()

    def prefix(self):
        return "*"

    def suffix(self):
        return ""

    def instantiate(self, variable):
        super().instantiate(variable)
        variable.__getitem__ = MethodType(self.getitem, variable)

    @staticmethod
    def getitem(self, index):
        from .. import expression as E
        return E.GetItem(self, index)

    def wrapped(self):
        return PointerType(self.base)

    def declare(self, name, init=None):
        return f"{self.base.cname()} {name}[{self.shape[0]}];"


def make_array_type(base, shape):
    if len(shape) == 1 and isinstance(shape[0], int):
        return SimpleArrayType(base, shape)
    else:
        return ComplexArrayType(base, shape)

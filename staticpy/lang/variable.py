from .value import Value
from . import expression as E


class Variable(Value):
    def __init__(self, name: str, type):
        self.name = name
        self.type = type

    def __str__(self):
        return str(self.name)


class ArrayVariable(Variable):
    class ShapeProxy:
        def __init__(self, var):
            self.var = var

        def __getitem__(self, i):
            return self.var._shape[i] if isinstance(i, int) else E.GetItem(E.GetAttr(self.var, "shape"), i)

    def __init__(self, name, type):
        super().__init__(name, type)
        self._shape = type.shape
        self.shape = ArrayVariable.ShapeProxy(self)
        self.dim = type.dim
        self.itemsize = type.itemsize

    def __getitem__(self, indices):
        indices = [x.value if isinstance(x, E.Const) else x for x in indices]
        return E.CallFunction(E.GetAttr(self, "getData"), indices)

    def __len__(self):
        return self.type.shape[0]


class Name(Value):
    def __init__(self, name: str):
        self.name = name

    def __str__(self):
        return str(self.name)

    def __eq__(self, other):
        return isinstance(other, Name) and self.name == other.name


def variable(name, type):
    return type.instantiate()(name, type)

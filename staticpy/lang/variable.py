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
            self._shape = var._shape

        def __len__(self):
            return len(self._shape)

        def __getitem__(self, i):
            if isinstance(i, int) and isinstance(self._shape[i], int):
                return self._shape[i]
            else:
                return E.GetItem(E.GetAttr(self.var, "shape"), i)

    def __init__(self, name, type):
        super().__init__(name, type)
        self._shape = type.shape
        self.shape = ArrayVariable.ShapeProxy(self)
        self.dim = type.dim
        self.itemsize = type.itemsize

    def __getitem__(self, indices):
        # TODO: optionally wrap-around indices
        if not isinstance(indices, tuple):
            indices = (indices, )
        indices = [x.value if isinstance(x, E.Const) else x for x in indices]
        if self.type.is_continuous:
            strides = [self.shape[i] for i in range(1, self.dim)] + [1]
            index = indices[0] * strides[0]
            for idx, stride in zip(indices[1:], strides[1:]):
                index = index + idx * stride
        else:
            strides = E.GetAttr(self, Name("strides"))
            index = E.GetItem(strides, E.Const(0)) * indices[0]
            for i, idx in enumerate(indices[1:], 1):
                index = index + E.GetItem(strides, E.Const(i)) * idx
            index = index / self.itemsize
        return E.GetItem(E.GetAttr(self, "data"), index)

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

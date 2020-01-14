import abc


class Value(abc.ABC):
    def __init__(self, type=None):
        self.type = type
        if hasattr(type, "v__init__"):
            type.v__init__(self)

    @abc.abstractmethod
    def __str__(self):
        pass

    def __getattr__(self, key):
        try:
            return super().__getattribute__(key)
        except AttributeError:
            name = "v_" + key
            if "type" in self.__dict__ and self.type is not None and name in self.type.__dict__:
                return getattr(self.type, "v_" + key)(self)
            else:
                raise

    def __call__(self, *args, **kwargs):
        from .expression import CallFunction
        if hasattr(self.type, "v__call__"):
            return self.type.v__call__(self, *args, **kwargs)
        else:
            return CallFunction(self, *args)

    def __getitem__(self, index):
        from .expression import GetItem
        if hasattr(self.type, "v__getitem__"):
            return self.type.v__getitem__(self, index)
        else:
            return GetItem(self, index)

    def __len__(self):
        if hasattr(self.type, "v__len__"):
            return self.type.v__len__(self)

    def astype(self, type):
        from . import expression as E
        return E.StaticCast(self, type)

    def __add__(self, other):
        if isinstance(other, int) and other == 0:
            return self
        from .expression import BinaryAdd
        return BinaryAdd(self, other)

    def __radd__(self, other):
        if isinstance(other, int) and other == 0:
            return self
        from .expression import BinaryAdd
        return BinaryAdd(other, self)

    def __sub__(self, other):
        if isinstance(other, int) and other == 0:
            return self
        from .expression import BinarySubtract
        return BinarySubtract(self, other)

    def __rsub__(self, other):
        from .expression import BinarySubtract
        return BinarySubtract(other, self)

    def __mul__(self, other):
        if isinstance(other, int) and other == 1:
            return self
        from .expression import BinaryMultiply
        return BinaryMultiply(self, other)

    def __rmul__(self, other):
        if isinstance(other, int) and other == 1:
            return self
        from .expression import BinaryMultiply
        return BinaryMultiply(other, self)

    def __div__(self, other):
        if isinstance(other, int) and other == 1:
            return self
        from .expression import BinaryDivide
        return BinaryDivide(self, other)

    def __rdiv__(self, other):
        from .expression import BinaryDivide
        return BinaryDivide(other, self)

    def __truediv__(self, other):
        from .expression import BinaryDivide
        return BinaryDivide(self, other)

    def __lshift__(self, other):
        from .expression import BinaryLShift
        return BinaryLShift(self, other)

    def __rshift__(self, other):
        from .expression import BinaryRShift
        return BinaryRShift(self, other)

    def __hash__(self):
        return hash(str(self))

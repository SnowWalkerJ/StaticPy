import abc


class Value(abc.ABC):
    @abc.abstractmethod
    def __str__(self):
        pass

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

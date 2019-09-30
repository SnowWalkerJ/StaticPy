import abc


class Value(abc.ABC):
    @abc.abstractmethod
    def __str__(self):
        pass

    def astype(self, type):
        from . import expression as E
        return E.Cast(self, type)

    def __add__(self, other):
        from .expression import BinaryAdd
        return BinaryAdd(self, other)

    def __sub__(self, other):
        from .expression import BinarySubtract
        return BinarySubtract(self, other)

    def __mul__(self, other):
        from .expression import BinaryMultiply
        return BinaryMultiply(self, other)

    def __div__(self, other):
        from .expression import BinaryDivide
        return BinaryDivide(self, other)

    def __truediv__(self, other):
        from .expression import BinaryDivide
        return BinaryDivide(self, other)

    def __lshift__(self, other):
        from .expression import BinaryLShift
        return BinaryLShift(self, other)

    def __rshift__(self, other):
        from .expression import BinaryRShift
        return BinaryRShift(self, other)

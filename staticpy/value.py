import abc


class Value(abc.ABC):
    @abc.abstractmethod
    def __str__(self):
        pass

    def astype(self, type):
        from . import expression as E
        return E.Cast(self, type)

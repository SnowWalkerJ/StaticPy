from abc import ABC, abstractmethod


class TypeBase(ABC):
    def __init__(self, name):
        self.name = name
        self.base = None

    def is_abstract(self):
        return True

    @abstractmethod
    def cname(self):
        pass

    @abstractmethod
    def prefix(self):
        pass

    @abstractmethod
    def suffix(self):
        pass

    def instantiate(self):
        from .. import variable as V
        return V.Variable

    def compatible(self, type):
        return False

    def __str__(self):
        return " ".join([str(self.cname()), self.prefix()])

    def declare(self, name, init=None):
        if init is None:
            return f"{self}{name};"
        else:
            return f"{self}{name} = {init};"

    def wrapped(self):
        return self

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

    def compatible(self, type):
        return False

    def __str__(self):
        prefix = self.prefix()
        if prefix:
            return " ".join([self.cname(), self.prefix()])
        else:
            return self.cname()

    def declare(self, name, init=None):
        return f"{self}{name}" + ("" if init is None else f" = {init}")

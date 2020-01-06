from abc import ABC, abstractmethod


class TypeBase(ABC):
    def __init__(self, name):
        self.name = name
        self.base = None
        self.is_primitive = False

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
        return " ".join([str(self.cname()), self.prefix()])

    def declare(self, name, init=None, qualifiers=[]):
        qualifiers = (" ".join(qualifiers) + " ") if qualifiers else ""
        if init is None:
            return f"{qualifiers}{self}{name};"
        else:
            return f"{qualifiers}{self}{name} = {init};"

    def wrapped(self):
        return self

    @property
    def ptr(self):
        return PointerType(self)

    @property
    def ref(self):
        return ReferenceType(self)


class PointerType(TypeBase):
    def __init__(self, base):
        self.base = base

    def cname(self):
        return self.base.cname()

    def prefix(self):
        return "*"

    def suffix(self):
        return ""

    def declare(self, name, init=None, qualifiers=[]):
        qualifiers = " ".join(qualifiers) + " " if qualifiers else ""
        if init is None:
            return f"{qualifiers}{self}{name} = nullptr;"
        else:
            return f"{qualifiers}{self}{name} = {init};"


class ReferenceType(TypeBase):
    def __init__(self, base):
        self.base = base

    def cname(self):
        return str(self.base.cname()) + "&"

    def prefix(self):
        return ""

    def suffix(self):
        return ""

    def declare(self, name, init=None, qualifiers=[]):
        if init is None:
            raise ValueError("Can't declare a reference without target")
        else:
            qualifiers = " ".join(qualifiers) + " " if qualifiers else ""
            return f"{qualifiers}{self}{name} = {init};"

from functools import partial

from .value import Value
from . import expression as E
from .type.derived import ArrayType


class Variable(Value):
    def __init__(self, name: str, type):
        self.name = name
        self.type = type
        type.instantiate(self)

    def __str__(self):
        return str(self.name)


class Name(Value):
    def __init__(self, name: str):
        self.name = name

    def __str__(self):
        return str(self.name)

    def __eq__(self, other):
        return isinstance(other, Name) and self.name == other.name

from ..session import get_session
from .base import TypeBase
from .array import ArrayType


class PrimitiveType(TypeBase):
    def __init__(self, name, base=None, ctype=None, size=None, compatible_type=None):
        self.name = f'nf.{name}'
        self.base = base
        self.ctype = ctype
        self.size = size
        self.compatible_type = compatible_type or (base.compatible_type if base is not None else None)

    def is_abstract(self):
        return not self.ctype

    def __getitem__(self, shape):
        if isinstance(shape, int):
            shape = (shape, )
        session = get_session()
        key = (self, shape)
        if key not in session.array_types:
            session.array_types[key] = ArrayType(self, shape)
        return session.array_types[key]

    def cname(self):
        return self.ctype

    def prefix(self):
        return ""

    def suffix(self):
        return ""

    def __equal__(self, other):
        return self is other

    def __repr__(self):
        return self.name

    def compatible(self, type):
        return type is self.compatible_type


Real = PrimitiveType("Real")

Integral = PrimitiveType("Integral", Real, compatible_type=int)
Bool = PrimitiveType("Bool", Integral, "bool", 1, bool)
Char = PrimitiveType("Char", Integral, "char", 1)
Short = PrimitiveType("Short", Integral, "short", 2)
Int = PrimitiveType("Int", Integral, "int", 4)
Long = PrimitiveType("Long", Integral, "long", 8)

Floating = PrimitiveType("Floating", Real, compatible_type=float)
Float = PrimitiveType("Float", Floating, "float", 4)
Double = PrimitiveType("Double", Floating, "double", 8)

Void = PrimitiveType("Void", None, "void", 0)

String = PrimitiveType("String", None, "std::string", 0, compatible_type=str)

BuiltInType = PrimitiveType("BuiltIn", None, "", 0)

default_types = {
    int: Long,
    float: Double,
    str: String,
}

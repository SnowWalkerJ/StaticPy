from ...session import get_session
from .base import TypeBase


class PrimitiveType(TypeBase):
    def __init__(self, name, base=None, ctype=None, size=None, compatible_type=None):
        self.name = f'staticpy.{name}'
        self.base = base
        self.ctype = ctype
        self.size = size
        self.is_primitive = True
        self.compatible_type = compatible_type or (base.compatible_type if base is not None else None)

    def is_abstract(self):
        return not self.ctype

    def __getitem__(self, shape):
        from .derived import ArrayType
        from .. import expression as E
        if not isinstance(shape, (list, tuple)):
            shape = (shape, )
        shape = tuple(x.value if isinstance(x, E.Const) else x for x in shape)
        if isinstance(shape[-1], bool):
            is_continuous = shape[-1]
            shape = shape[:-1]
            if is_continuous and any(not isinstance(x, int) for x in shape[1:]):
                raise TypeError("continuous array requires constant shape except for the first dimension")
        else:
            is_continuous = False
        shape = tuple(s if isinstance(s, int) else ... for s in shape)
        session = get_session()
        key = (self, shape, is_continuous)
        return ArrayType(self, shape, is_continuous)
        # if key not in session.array_types:
        #     session.array_types[key] = ArrayType(self, shape, is_continuous)
        # return session.array_types[key]

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

BuiltInType = PrimitiveType("BuiltIn", None, "", 0)

AutoType = PrimitiveType("auto", None, "auto", 0)

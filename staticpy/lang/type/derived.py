# TODO: list and dict
from types import MethodType

from .base import TypeBase
from ..variable import Name


class DerivedType(TypeBase):
    pass


class OtherType(DerivedType):
    def __init__(self, alias):
        self.real_type = alias

    def cname(self):
        return str(self.real_type)

    def prefix(self):
        return ""

    def suffix(self):
        return ""


class ArrayType(DerivedType):
    def __init__(self, base, shape, is_continuous):
        self.base = base
        self.shape = shape
        self.dim = len(shape)
        self.itemsize = base.size
        self.is_continuous = is_continuous

    def instantiate(self):
        from .. import variable as V
        return V.ArrayVariable

    def cname(self):
        from .. import expression as E, variable as V
        return E.TemplateInstantiate(V.Name("Array"), (self.base, len(self.shape)))

    def prefix(self):
        return ""

    def suffix(self):
        return ""

    def wrapped(self):
        from .. import expression as E, variable as V
        clas = E.ScopeAnalysis(V.Name("py"), V.Name("buffer"))
        return OtherType(clas)


class UserDefinedClassVariableMeta(type):
    def __new__(cls, name, ctype):
        from .. import expression as E, variable as V
        bases = (V.Variable, )
        name = str(name)
        members = {pyname: cls.make_member(cname) for pyname, cname in ctype.members.items()}

        def __init__(self, name, ctype):
            V.Variable.__init__(self, name, ctype)

        members['__init__'] = __init__
        return type(name, bases, members)

    @staticmethod
    def make_member(member):
        from .. import expression as E, variable as V

        if isinstance(member, str):
            def f(self, *args):
                return E.CallFunction(E.GetAttr(self.name, member), args)
        else:
            def f(self, *args):
                return member(self, *args)

        return f


class UserDefinedClassType(DerivedType):
    def __init__(self, name, namespace, members):
        self.name = name
        self.members = members
        self.namespace = namespace
        self.variable_class = UserDefinedClassVariableMeta(name, self)

    def cname(self):
        from .. import expression as E, variable as V
        return str(V.Name(self.name) if self.namespace is None else E.ScopeAnalysis(self.namespace, self.name))

    def prefix(self):
        return ""

    def suffix(self):
        return ""

    def instantiate(self):
        return self.variable_class

    def __getitem__(self, *args):
        from .. import expression as E
        return UserDefinedClassType(E.TemplateInstantiate(self.name, args), self.members, self.namespace)


class StringType(UserDefinedClassType):
    def __init__(self):
        name = "string"
        namespace = "std"
        members = {"__len__": "size", "startswith": "starts_with", "endswith": "ends_with"}
        super().__init__(name, namespace, members)


AutoType = OtherType(Name("auto"))
String = StringType()

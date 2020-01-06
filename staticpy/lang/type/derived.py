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
    class ShapeProxy:
        def __init__(self, var):
            self.var = var
            self._shape = var._shape

        def __len__(self):
            return len(self._shape)

        def __getitem__(self, i):
            from .. import expression as E
            if isinstance(i, int) and isinstance(self._shape[i], int):
                return self._shape[i]
            else:
                return E.GetItem(E.GetAttr(self.var, "shape"), i)

    def __init__(self, base, shape, is_continuous):
        self.base = base
        self.shape = shape
        self.dim = len(shape)
        self.itemsize = base.size
        self.is_continuous = is_continuous

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

    def v__init__(t, self):
        self._shape = t.shape
        self.shape = ArrayType.ShapeProxy(self)
        self.dim = t.dim
        self.itemsize = t.itemsize

    def v__getitem__(t, self, indices):
        from .. import expression as E
        # TODO: optionally wrap-around indices
        if not isinstance(indices, tuple):
            indices = (indices, )
        indices = [x.value if isinstance(x, E.Const) else x for x in indices]
        if self.type.is_continuous:
            strides = [self.shape[i] for i in range(1, self.dim)] + [1]
            index = indices[0] * strides[0]
            for idx, stride in zip(indices[1:], strides[1:]):
                index = index + idx * stride
        else:
            strides = E.GetAttr(self, Name("strides"))
            index = E.GetItem(strides, E.Const(0)) * indices[0]
            for i, idx in enumerate(indices[1:], 1):
                index = index + E.GetItem(strides, E.Const(i)) * idx
            index = index / self.itemsize
        return E.GetItem(E.GetAttr(self, "data"), index)

    def v__len__(t, self):
        return t.shape[0]


def method_wrapper(fn):
    def decorator(self):
        def wrapped(*args, **kwargs):
            return fn(self, *args, **kwargs)
        return wrapped
    return decorator


class UserDefinedClassType(DerivedType):
    def __init__(self, name, namespace, members):
        self.name = name
        self.members = members
        self.namespace = namespace
        for pyname, cname in members.items():
            prefix = "v" if pyname[:2] == "__" else "v_"
            setattr(self, prefix + pyname, self.make_member(pyname, cname))

    @staticmethod
    def make_member(pyname, member):
        from .. import expression as E, variable as V

        if isinstance(member, str):
            def f(self, *args):
                return E.CallFunction(E.GetAttr(self.name, member), args)
        else:
            def f(self, *args):
                return member(self, *args)

        return f if pyname[:2] == "__" else method_wrapper(f)

    def cname(self):
        from .. import expression as E, variable as V
        return str(V.Name(self.name) if self.namespace is None else E.ScopeAnalysis(self.namespace, self.name))

    def prefix(self):
        return ""

    def suffix(self):
        return ""

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

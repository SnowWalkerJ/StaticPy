from ..lang import variable as V, expression as E, type as T


class Object:
    def __init__(self, name, members):
        self.name = name
        for name, member in members.items():
            setattr(self, name, self._get_member(member))

    def _get_member(self, member):
        obj = self.static_attribute(member['name']) if member['static'] else self.dynamic_attribute(member['name'])
        if member['type'] == "method":
            def fn(*args):
                return E.CallFunction(obj, args)
            return fn
        else:
            return obj

    def dynamic_attribute(self, attr):
        return E.GetAttr(V.variable('this', T.PointerType(T.OtherType(self.name))), attr)

    def static_attribute(self, attr):
        return E.ScopeAnalysis(V.Name(self.name), V.Name(attr))


class Self(Object):
    def __str__(self):
        return "*this"


class Cls(Object, T.OtherType):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.real_type = V.Name(self.name)

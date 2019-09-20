import abc


class Statement(abc.ABC):
    pass


class Assign(Statement):
    def __init__(self, target, expr):
        self.target = target
        self.expr = expr


class SetAttr(Statement):
    def __init__(self, obj, attr, value):
        self.obj = obj
        self.attr = attr
        self.value = value


class SetItem(Statement):
    def __init__(self, obj, index, value):
        self.obj = obj
        self.index = index
        self.value = value


class ReturnValue(Statement):
    def __init__(self, expr):
        self.expr = expr


class ExpressionStatement(Statement):
    def __init__(self, expr):
        self.expr = expr


class Continue(Statement):
    pass


class Break(Statement):
    pass


def from_expression(expr):
    return ExpressionStatement(expr)

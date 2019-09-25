import abc

from .value import Value
from . import type as T


class Expression(Value):
    pass


class OpExpression(Expression):
    level = 0

    def add_bracket(self, other):
        if isinstance(other, OpExpression) and other.level <= self.level:
            return f"({other})"
        else:
            return str(other)


def unary_expression(name, op, level=None):
    class UnaryExpression(OpExpression):
        op = op
        name = name
        level = level

        def __init__(self, item):
            self.item = self.add_bracket(cast_value_to_expression(item))

        def __repr__(self):
            return f"{self.name}({self.item})"

        def __str__(self):
            return f"{self.op}({self.item})"

    return UnaryExpression


def binary_expression(name, op, level=None):
    class BinaryExpression(OpExpression):
        op = op
        name = name
        level = level

        def __init__(self, item1, item2):
            self.item1 = self.add_bracket(cast_value_to_expression(item1))
            self.item2 = self.add_bracket(cast_value_to_expression(item2))

        def __repr__(self):
            return f"{self.name}({self.item1}, {self.item2})"

        def __str__(self):
            return f"{self.item1} {self.op} {self.item2}"

    return BinaryExpression


def compare_expression(name, op, level=None):
    class BinaryExpression(OpExpression):
        op = op
        name = name
        level = level

        def __init__(self, item1, item2):
            self.item1 = self.add_bracket(cast_value_to_expression(item1))
            self.item2 = self.add_bracket(cast_value_to_expression(item2))

        def __repr__(self):
            return f"{self.item1} {self.op} {self.item2}"

        def __str__(self):
            return f"{self.item1} {self.op} {self.item2}"

    return BinaryExpression


UnaryPositive = unary_expression('UnaryPositive', '+', 5)
UnaryNegative = unary_expression('UnaryNegative', '-', 5)
UnaryNot = unary_expression('UnaryNot', '!', 16)
UnaryInvert = unary_expression('UnaryInvert', '~')
BinaryMultiply = binary_expression('BinaryMultiply', '*', 14)
BinaryDivide = binary_expression('BinaryDivide', '/', 14)
BinaryModulo = binary_expression('BinaryModulo', '%', 14)
BinaryAdd = binary_expression('BinaryAdd', '+', 13)
BinarySubtract = binary_expression('BinarySubtract', '-', 13)
BinaryLShift = binary_expression('BinaryLShift', '<<', 12)
BinaryRShift = binary_expression('BinaryRShift', '>>', 12)
BinaryAnd = binary_expression('BinaryAdd', '&', 8)
BinaryXor = binary_expression('BinaryXor', '^')
BinaryOr = binary_expression('BinaryOr', '|', 7)
LogicalAnd = binary_expression('LogicalAnd', '&&', 6)
LogicalOr = binary_expression('LogicalOr', '||', 5)
CompareGT = compare_expression('GreaterThan', '>', 11)
CompareLT = compare_expression('LessThan', '<', 11)
CompareGE = compare_expression('GreaterEqual', '>=', 11)
CompareLE = compare_expression('LessEqual', '<=', 11)
CompareEQ = compare_expression('Equal', '==', 11)
CompareNE = compare_expression('NotEqual', '!=', 11)


class IIf(OpExpression):
    level = 17

    def __init__(self, condition, value_if_true, value_if_false):
        self.condition = self.add_bracket(cast_value_to_expression(condition))
        self.value_if_true = self.add_bracket(cast_value_to_expression(value_if_true))
        self.value_if_false = self.add_bracket(cast_value_to_expression(value_if_false))

    def __str__(self):
        return f"{self.condition} ? {self.value_if_true} : {self.value_if_false}"


class CallFunction(Expression):
    def __init__(self, func, args):
        self.func = func
        self.args = tuple(map(cast_value_to_expression, args))
        super().__init__()

    def __str__(self):
        name = self.func
        args = ", ".join(map(str, self.args))
        return f"{name}({args})"


class Const(Expression):
    def __init__(self, value):
        self.value = value
        self.type = self.infer_type(value)

    @staticmethod
    def infer_type(value):
        if isinstance(value, int):
            return T.Integral
        elif isinstance(value, float):
            return T.Floating
        elif isinstance(value, bool):
            return T.Bool
        elif isinstance(value, str):
            return T.String
        else:
            raise TypeError(f"type '{type(value)} not supported")

    def __str__(self):
        if self.type is T.String:
            value = self.value.replace("\\", "\\\\").replace("\"", "\\\"")
            return f'"{value}"'
        else:
            return str(self.value).lower()


class Var(Expression):
    def __init__(self, variable):
        self.variable = variable

    def __str__(self):
        return str(self.variable)


class GetAttr(Expression):
    level = 19

    def __init__(self, obj, attr):
        self.obj = obj
        self.attr = attr

    def __str__(self):
        return ".".join(map(str, [self.obj, self.attr]))


class GetItem(Expression):
    level = 19

    def __init__(self, obj, index):
        self.obj = obj
        self.index = index

    def __str__(self):
        return f"{self.obj}[{self.index}]"


class Cast(Expression):
    level = 19

    def __init__(self, expr: Expression, astype):
        assert isinstance(astype, T.PrimitiveType), "can only cast to basic type"
        self.expr = cast_value_to_expression(expr)
        self.astype = astype
        self.type = type

    def __str__(self):
        return f"static_cast<{self.astype.cname()}>({self.expr})"


def compare_op(opname):
    mapping = {
        '>': CompareGT,
        '<': CompareLT,
        '>=': CompareGE,
        '<=': CompareLE,
        '==': CompareEQ,
    }
    return mapping[opname]


def cast_value_to_expression(value):
    from .variable import Variable
    if isinstance(value, Expression):
        pass
    elif isinstance(value, Variable):
        value = Var(value)
    else:
        value = Const(value)
    return value

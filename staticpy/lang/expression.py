import abc

from .value import Value
from . import type as T
from .common.string import stringify_arguments


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
    my_name = name
    my_op = op
    my_level = level

    class UnaryExpression(OpExpression):
        op = my_op
        name = my_name
        level = my_level

        def __init__(self, item):
            self.item = self.add_bracket(cast_value_to_expression(item))
            super().__init__()

        def __repr__(self):
            return f"{self.name}({self.item})"

        def __str__(self):
            return f"{self.op}({self.item})"

    return UnaryExpression


def binary_expression(name, op, level=None):
    my_name = name
    my_op = op
    my_level = level

    class BinaryExpression(OpExpression):
        op = my_op
        name = my_name
        level = my_level

        def __init__(self, item1, item2):
            self.item1 = self.add_bracket(cast_value_to_expression(item1))
            self.item2 = self.add_bracket(cast_value_to_expression(item2))
            super().__init__()

        def __repr__(self):
            return f"{self.name}({self.item1}, {self.item2})"

        def __str__(self):
            return f"{self.item1} {self.op} {self.item2}"

    return BinaryExpression


def compare_expression(name, op, level=None):
    my_name = name
    my_op = op
    my_level = level

    class BinaryExpression(OpExpression):
        op = my_op
        name = my_name
        level = my_level

        def __init__(self, item1, item2):
            self.item1 = self.add_bracket(cast_value_to_expression(item1))
            self.item2 = self.add_bracket(cast_value_to_expression(item2))
            super().__init__()

        def __repr__(self):
            return f"{self.item1} {self.op} {self.item2}"

        def __str__(self):
            return f"{self.item1} {self.op} {self.item2}"

    return BinaryExpression


UnaryPositive = unary_expression('UnaryPositive', '+', 16)
UnaryNegative = unary_expression('UnaryNegative', '-', 16)
UnaryNot = unary_expression('UnaryNot', '!', 16)
UnaryInvert = unary_expression('UnaryInvert', '~', 16)
BinaryMultiply = binary_expression('BinaryMultiply', '*', 14)
BinaryDivide = binary_expression('BinaryDivide', '/', 14)
BinaryModulo = binary_expression('BinaryModulo', '%', 14)
BinaryAdd = binary_expression('BinaryAdd', '+', 13)
BinarySubtract = binary_expression('BinarySubtract', '-', 13)
BinaryLShift = binary_expression('BinaryLShift', '<<', 12)
BinaryRShift = binary_expression('BinaryRShift', '>>', 12)
BinaryAnd = binary_expression('BinaryAdd', '&', 8)
BinaryXor = binary_expression('BinaryXor', '^', 7)
BinaryOr = binary_expression('BinaryOr', '|', 7)
LogicalAnd = binary_expression('LogicalAnd', '&&', 6)
LogicalOr = binary_expression('LogicalOr', '||', 5)
CompareGT = compare_expression('GreaterThan', '>', 11)
CompareLT = compare_expression('LessThan', '<', 11)
CompareGE = compare_expression('GreaterEqual', '>=', 11)
CompareLE = compare_expression('LessEqual', '<=', 11)
CompareEQ = compare_expression('Equal', '==', 11)
CompareNE = compare_expression('NotEqual', '!=', 11)


class AddressOf(OpExpression):
    op = "&"
    name = "AddressOf"
    level = 16

    def __init__(self, item):
        self.item = cast_value_to_expression(item)
        type = self.item.type.ptr() if self.item.type is not None else None
        super().__init__(type)

    def __repr__(self):
        return f"{self.name}({self.item})"

    def __str__(self):
        return f"{self.op}{self.item}"


class ScopeAnalysis(OpExpression):
    op = "::"
    name = "ScopeAnalysis"
    level = 18

    def __init__(self, item1, item2):
        self.item1 = item1
        self.item2 = item2
        super().__init__()

    def __repr__(self):
        return f"{self.name}({self.item1}, {self.item2})"

    def __str__(self):
        return f"{self.item1}{self.op}{self.item2}"


class IIf(OpExpression):
    level = 17

    def __init__(self, condition, value_if_true, value_if_false):
        self.condition = self.add_bracket(cast_value_to_expression(condition))
        self.value_if_true = self.add_bracket(cast_value_to_expression(value_if_true))
        self.value_if_false = self.add_bracket(cast_value_to_expression(value_if_false))
        super().__init__()

    def __str__(self):
        return f"{self.condition} ? {self.value_if_true} : {self.value_if_false}"


class CallFunction(Expression):
    def __init__(self, func, args, type=None):
        self.func = func
        self.args = tuple(map(cast_value_to_expression, args))
        super().__init__(type)

    def __str__(self):
        name = self.func
        args = ", ".join(map(str, self.args))
        return f"{name}({args})"


class TemplateInstantiate(Expression):
    def __init__(self, name, args):
        self.name = name
        self.args = args
        super().__init__()

    def __str__(self):
        args = "<" + stringify_arguments(self.args) + ">"
        return str(self.name) + args


class Const(Expression):
    def __init__(self, value):
        self.value = value
        super().__init__(self.infer_type(value))

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
        elif isinstance(value, T.TypeBase):
            return T.TypeBase
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
        super().__init__(variable.type)

    def __str__(self):
        return str(self.variable)


class GetAttr(Expression):
    level = 19

    def __init__(self, obj, attr, symbol=None):
        self.obj = obj
        self.attr = attr
        if symbol is None:
            if hasattr(obj, "type") and isinstance(obj.type, T.PointerType):
                symbol = "->"
            else:
                symbol = "."
        self.symbol = symbol

    def __str__(self):
        return self.symbol.join(map(str, [self.obj, self.attr]))


class GetItem(Expression):
    level = 19

    def __init__(self, obj, index):
        self.obj = obj
        self.index = index
        super().__init__()

    def __str__(self):
        return f"{self.obj}[{self.index}]"


class StaticCast(Expression):
    level = 19

    def __init__(self, expr: Expression, astype):
        self.expr = cast_value_to_expression(expr)
        super().__init__(astype)

    def __str__(self):
        return f"static_cast<{self.type}>({self.expr})"


class Cast(Expression):
    level = 19

    def __init__(self, expr: Expression, astype):
        self.expr = cast_value_to_expression(expr)
        super().__init__(astype)

    def __str__(self):
        return f"({self.type})({self.expr})"


class initializer_list(Expression):
    level = 19

    def __init__(self, *args):
        self.args = args

    def __str__(self):
        return "{" + ", ".join(map(str, self.args)) + "}"


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
    from .variable import Variable, Name
    if isinstance(value, Expression):
        pass
    elif isinstance(value, (Variable, Name)):
        value = Var(value)
    else:
        value = Const(value)
    return value

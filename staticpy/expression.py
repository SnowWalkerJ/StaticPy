import abc

from .value import Value


class Expression(Value):
    pass
    # @abc.abstractmethod
    # def translate_pure(self):
    #     pass

    # @abc.abstractmethod
    # def translate_hybrid(self):
    #     pass


def unary_expression(name, op):
    class UnaryExpression(Expression):
        op = op
        name = name

        def __init__(self, item):
            self.item = item

        def __repr__(self):
            return f"{self.name}({self.item})"
    return UnaryExpression


def binary_expression(name, op):
    class BinaryExpression(Expression):
        op = op
        name = name

        def __init__(self, item1, item2):
            self.item1 = item1
            self.item2 = item2

        def __repr__(self):
            return f"{self.name}({self.item1}, {self.item2})"
    return BinaryExpression


def compare_expression(name, op):
    class BinaryExpression(Expression):
        op = op
        name = name

        def __init__(self, item1, item2):
            self.item1 = item1
            self.item2 = item2

        def __repr__(self):
            return f"{self.item1} {self.op} {self.item2}"
    return BinaryExpression


UnaryPositive = unary_expression('UnaryPositive', '+')
UnaryNegative = unary_expression('UnaryNegative', '-')
UnaryNot = unary_expression('UnaryNot', '!')
UnaryInvert = unary_expression('UnaryInvert', '~')
BinaryMultiply = binary_expression('BinaryMultiply', '*')
BinaryModulo = binary_expression('BinaryModulo', '%')
BinaryAdd = binary_expression('BinaryAdd', '+')
BinarySubtract = binary_expression('BinarySubtract', '-')
BinaryLShift = binary_expression('BinaryLShift', '<<')
BinaryRShift = binary_expression('BinaryRShift', '>>')
BinaryAnd = binary_expression('BinaryAdd', '&&')
BinaryXor = binary_expression('BinaryXor', '^')
BinaryOr = binary_expression('BinaryOr', '||')
CompareGT = compare_expression('GreaterThan', '>')
CompareLT = compare_expression('LessThan', '<')
CompareGE = compare_expression('GreaterEqual', '>=')
CompareLE = compare_expression('LessEqual', '<=')
CompareEQ = compare_expression('Equal', '==')


class CallFunction(Expression):
    def __init__(self, func, args):
        self.func = func
        self.args = args
        super().__init__()


class Const(Expression):
    def __init__(self, value):
        self.value = value


class GetAttr(Expression):
    def __init__(self, obj, attr):
        self.obj = obj
        self.attr = attr


def compare_op(opname):
    mapping = {
        '>': CompareGT,
        '<': CompareLT,
        '>=': CompareGE,
        '<=': CompareLE,
        '==': CompareEQ,
    }
    return mapping[opname]

class Expression:
    pass


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


UnaryPositive = unary_expression('UnaryPositive', '+')
UnaryNegative = unary_expression('UnaryNegative', '-')
UnaryNot = unary_expression('UnaryNot', '!')
UnaryInvert = unary_expression('UnaryInvert', '~')
BinaryMultiply = binary_expression('BinaryMultiply', '*')
BinaryModulo = binary_expression('BinaryModulo', '%')
BinaryAdd = binary_expression('BinaryAdd', '+')
BinarySubtract = binary_expression('BinarySubtract', '-')

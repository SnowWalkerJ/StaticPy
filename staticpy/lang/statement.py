import abc
import typing

from . import expression as E
from .common import auto_add


class Statement(abc.ABC):
    @abc.abstractmethod
    def translate(self) -> typing.List[str]:
        pass


class VariableDeclaration(Statement):
    def __init__(self, var):
        self.variable = var

    def translate(self):
        var = self.variable
        return [f"{var.type.cname()} {var.name};"]


class UsingNamespace(Statement):
    def __init__(self, namespace):
        self.namespace = namespace

    def translate(self):
        return [f"using namespace {self.namespace};"]


class SimpleStatement(Statement):
    def __init__(self, stmt: str):
        self.statement = stmt

    def translate(self):
        return [self.statement]


class Assign(Statement):
    def __init__(self, target, expr):
        self.target = target
        self.expr = expr

    def translate(self):
        return [f"{self.target} = {self.expr};"]


class SetAttr(Statement):
    def __init__(self, obj, attr, value):
        self.obj = obj
        self.attr = attr
        self.value = value

    def translate(self):
        return [f"{self.obj}.{self.attr} = {self.value};"]


class SetItem(Statement):
    def __init__(self, obj, index, value):
        self.obj = obj
        self.index = index
        self.value = value

    def translate(self):
        return [f"{self.obj}[{self.index}] = {self.value};"]


class ReturnValue(Statement):
    def __init__(self, expr):
        self.expr = expr

    def translate(self):
        return [f"return {self.expr};"]


class ExpressionStatement(Statement):
    def __init__(self, expr):
        self.expr = expr

    def translate(self):
        return [str(self.expr) + ";"]


class Continue(Statement):
    def translate(self):
        return ["continue;"]


class Break(Statement):
    def translate(self):
        return ["break;"]


class BlockStatement(Statement):
    def __init__(self, block):
        self.block = block

    def translate(self):
        return ["  " + line for line in self.block.translate()]


def inplace_statement(name, op):
    my_name = name
    my_op = op

    class InplaceStatement(Statement):
        name = my_name
        op = my_op

        def __init__(self, target, expr: E.Expression):
            self.target = target
            self.expr = E.cast_value_to_expression(expr)

        def translate(self):
            return [f"{self.target} {self.op} {self.expr};"]

        def __repr__(self):
            return f"{self.name}({self.target}, {self.expr})"

    return InplaceStatement


class SingleLineComment(Statement):
    def __init__(self, text):
        self.text = text

    def translate(self):
        return ["// " + str(self.text)]


class BlockComment(Statement):
    def __init__(self, texts):
        self.texts = texts

    def translate(self):
        lines = []
        for i, line in enumerate(self.texts):
            prefix = "/* " if i == 0 else " * "
            lines.append(prefix + line)
        lines.append(" */")
        return lines


InplaceLShift = inplace_statement("InplaceLShift", "<<=")
InplaceRShift = inplace_statement("InplaceRShift", ">>=")
InplaceAdd = inplace_statement("InplaceAdd", "+=")
InplaceSubtract = inplace_statement("InplaceSubtract", "-=")
InplaceMultiply = inplace_statement("InplaceMultiply", "*=")
InplaceDivide = inplace_statement("InplaceDivide", "/=")
InplaceModulo = inplace_statement("InplaceModulo", "%=")
InplaceAnd = inplace_statement("InplaceAnd", "&=")
InplaceXor = inplace_statement("InplaceXor", "^=")
InplaceOr = inplace_statement("InplaceOr", "|=")


def from_expression(expr):
    return ExpressionStatement(expr)


as_statement = auto_add(from_expression)


@auto_add
def returns(expr):
    return ReturnValue(expr)


@auto_add
def assign(var, expr):
    return Assign(var, expr)


@auto_add
def using_namespace(name):
    return UsingNamespace(name)


@auto_add
def comment(text):
    if isinstance(text, str) and "\n" in text:
        text = text.split()
    if isinstance(text, list):
        return BlockComment(text)
    else:
        return SingleLineComment(text)


@auto_add
def statement(stmt):
    return SimpleStatement(stmt)

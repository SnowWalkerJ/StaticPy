from .session import get_session
from .statement import Statement
from .block import Block


class Macro:
    pass


class StatementMacro(Macro, Statement):
    def __init__(self, name, *args):
        self.name = name
        self.args = args
        super().__init__()

    def translate(self):
        args = " ".join(map(str, self.args))
        return [f"#{self.name} {args}"]


class IfDefMacro(Macro, Block):
    def __init__(self, symbol):
        self.symbol = symbol
        super().__init__()

    def translate(self):
        stmts = [f"#ifdef {self.symbol}"]
        stmts.extend(super().translate())
        stmts.append("#endif")
        return stmts


def include(name):
    if not (name[0] == "<" and name[-1] == ">"):
        name = "\"" + name + "\""
    return StatementMacro("include", name)


def defineM(name, value=None):
    if value is not None:
        return StatementMacro("define", name, value)
    else:
        return StatementMacro("define", name)


def undefineM(name):
    return StatementMacro("undef", name)


def ifdefM(name):
    return StatementMacro("ifdef", name)


def ifndefM(name):
    return StatementMacro("ifndef", name)


def elseM(name):
    return StatementMacro("else")


def endifM(name):
    return StatementMacro("endif")


def ifdefBM(name):
    return IfDefMacro(name)

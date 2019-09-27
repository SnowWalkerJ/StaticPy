from .session import get_session
from .statement import Statement, auto_add
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


@auto_add
def include(name):
    if not (name[0] == "<" and name[-1] == ">"):
        name = "\"" + name + "\""
    return StatementMacro("include", name)


@auto_add
def defineM(name, value=None):
    if value is not None:
        return StatementMacro("define", name, value)
    else:
        return StatementMacro("define", name)


@auto_add
def undefineM(name):
    return StatementMacro("undef", name)


@auto_add
def ifdefM(name):
    return StatementMacro("ifdef", name)


@auto_add
def ifndefM(name):
    return StatementMacro("ifndef", name)


@auto_add
def elseM(name):
    return StatementMacro("else")


@auto_add
def endifM(name):
    return StatementMacro("endif")


@auto_add
def ifdefBM(name):
    return IfDefMacro(name)

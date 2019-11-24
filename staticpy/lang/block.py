import abc
import itertools


class Block(abc.ABC):
    def __init__(self, statements=None):
        self.statements = statements or []

    @abc.abstractmethod
    def translate(self):
        return list(itertools.chain(*(stmt.translate() for stmt in self.statements)))

    def __enter__(self):
        from ..session import get_session
        get_session().push_block(self)

    def __exit__(self, *args):
        from ..session import get_session
        get_session().pop_block()

    def add_statement(self, stmt):
        self.statements.append(stmt)


class EmptyBlock(Block):
    def translate(self):
        return list(itertools.chain(*(stmt.translate() for stmt in self.statements)))


class Scope(Block):
    @abc.abstractmethod
    def translate(self):
        statements = []
        statements.append(self.prefix())
        for stmt in self.statements:
            for sub in stmt.translate():
                statements.append('  ' + sub)
        statements.append(self.suffix())
        return statements

    def prefix(self):
        return "{"

    def suffix(self):
        return "}"


class If(Scope):
    def __init__(self, condition, statements):
        self.condition = condition
        super().__init__(statements)

    def translate(self):
        return super().translate()

    def prefix(self):
        return f"if({self.condition}) {{"


class Else(Scope):
    def __init__(self, statements):
        super().__init__(statements)

    def translate(self):
        return super().translate()

    def prefix(self):
        return "else {"


class For(Scope):
    def __init__(self, variable, start, stop, step, statements):
        self.variable = variable
        self.start = start
        self.stop = stop
        self.step = step
        super().__init__(statements)

    def translate(self):
        return super().translate()

    def prefix(self):
        var = self.variable
        start = self.start
        stop = self.stop
        step = self.step
        steping = f"{var} += {step}"
        if step == 1:
            steping = f"{var}++"
        elif step == -1:
            steping = f"{var}--"
        return f"for({var} = {start}; {var} < {stop}; {steping}) {{"


class While(Scope):
    def __init__(self, condition, statements):
        self.condition = condition
        super().__init__(statements)

    def translate(self):
        return super().translate()

    def prefix(self):
        return f"while({self.condition}) {{"


class Function(Scope):
    def __init__(self, name, inputs, output, statements, is_method=False, is_constructor=False):
        self.name = name
        self.inputs = inputs
        self.output = output
        self.is_method = is_method
        self.is_constructor = is_constructor
        super().__init__(statements)

    def translate(self):
        return super().translate()

    def prefix(self):
        ret_type = "" if self.is_constructor else str(self.output)
        args = ", ".join(f"{type.cname()} {type.prefix()}{name}" for type, name in self.inputs)
        return f"{ret_type}{self.name}({args}) {{"

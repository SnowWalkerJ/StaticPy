import abc


class Block(abc.ABC):
    def __init__(self, statements):
        self.statements = statements

    @abc.abstractmethod
    def translate(self):
        pass

    def prefix(self):
        return ""

    def suffix(self):
        return ""


class Scope(Block):
    @abc.abstractmethod
    def translate(self):
        return [self.prefix()] + ["  " + stmt.translate() for stmt in self.statements] + [self.suffix()]

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

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

class Function(Scope):
    def __init__(self, name, inputs, output, statements, is_method=False, is_constructor=False):
        self.name = name
        self.inputs = inputs
        self.output = output
        self.is_method = is_method
        self.is_constructor = is_constructor
        super().__Init__(statements)
        
    def translate(self):
        return super().translate()
    
    def prefix(self):
        ret_type = "" if self.is_constructor else f"{self.output} "
        args = ", ".join(f"{type.cname()} {name}" for type, name in self.inputs)
        return f"{ret_type}{self.name}({args}) {{"

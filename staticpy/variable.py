from .value import Value


class Variable(Value):
    def __init__(self, name: str, type):
        self.name = name
        self.type = type

    def __str__(self):
        return str(self.name)


class Name(Value):
    def __init__(self, name: str):
        self.name = name

    def __str__(self):
        return str(self.name)

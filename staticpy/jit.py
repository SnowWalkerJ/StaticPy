class Function:
    def __init__(self, func):
        self.name = func.__name__
        self.funcs = [func]

    def overload(self, func):
        raise NotImplementedError

    def __call__(self, *args):
        pass

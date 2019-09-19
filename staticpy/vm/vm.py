import abc
import dis
import inspect


class VM(abc.ABC):
    __handlers = []

    def __init__(self):
        self.block_stack = []
        self.data_stack = []
        self.statements = []
        self.__variables = {}
        self.__load_handlers()

    def push(self, eos):
        self.data_stack.append(eos)

    def pop(self):
        return self.data_stack.pop()

    def pushn(self, *args):
        self.data_stack.extend(list(args))

    def popn(self, n):
        retvalues = self.data_stack[-n:]
        self.data_stack[-n:] = []
        return retvalues

    def gethandler(self, opcode):
        return self.__handlers[opcode]

    def get_variable(self, name):
        return self.__variables[name]

    def add_statement(self, stmt):
        self.statements.append(stmt)

    @classmethod
    def __load_handlers(cls):
        from . import handlers, constant
        tmp = []
        for name, value in inspect.getmembers(constant):
            tmp.append((value, getattr(handlers, name.lower(), handlers.not_implemented)))
        tmp.sort()
        cls.__handlers = [x[1] for x in tmp]

    @abc.abstractmethod
    def run(self):
        pass


class FunctionVM(VM):
    def __init__(self, func):
        self.func = func
        super().__init__()
        self.__source = None

    def run(self):
        self.resolve_annotations()
        for instruction in dis.get_instructions(self.code):
            opcode = instruction.opcode
            argval = instruction.argval
            offset = instruction.offset
            starts_line = instruction.starts_line
            is_jump_target = instruction.is_jump_target
            if starts_line is not None:
                self.add_source(starts_line)
            print(instruction)
            # handler = self.gethandler(opcode)
            # handler(self, argval)

    def resolve_annotations(self):
        """Resolve in-function annotations with regex"""
        pass

    def add_source(self, line):
        pass

    @property
    def source(self):
        if self.__source is None:
            self.__source = inspect.getsource(self.func)
        return self.__source

    @property
    def annotation(self):
        return self.func.__annotations__

    @property
    def code(self):
        return self.func.__code__

    @property
    def names(self):
        return self.code.co_names

    @property
    def varnames(self):
        return self.code.co_varnames

    @property
    def consts(self):
        return self.code.co_consts

    @property
    def signature(self):
        return inspect.signature(self.func)

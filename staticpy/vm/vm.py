import abc
import dis
import enum
import inspect


class BlockType(enum.IntEnum):
    Class = enum.auto
    Function = enum.auto
    Loop = enum.auto
    If = enum.auto
    Try = enum.auto
    Except = enum.auto
    Finally = enum.auto


class LoopType(enum.IntEnum):
    ForRange = enum.auto
    While = enum.auto


class Block:
    def __init__(self, type=None):
        self.type = type
        self.statements = []
        self.extra_info = {}

    def translate(self) -> str:
        pass


class InstructionQueue:
    def __init__(self, instruction: dis.Instruction):
        self.instruction = instruction
        self.instructions = [(instruction.opcode, instruction.argval)]

    @property
    def offset(self):
        return self.instruction.offset

    def inject_before(self, opcode, argval):
        self.instructions.insert(0, (opcode, argval))

    def inject_after(self, opcode, argval):
        self.instructions.append((opcode, argval))

    def inject_replace(self, opcode, argval):
        self.instructions = [(opcode, argval)]

    def reset(self):
        self.instructions = [(self.instruction.opcode, self.instruction.argval)]

    def run(self, vm):
        for opcode, argval in self.instructions:
            handler = vm.gethandler(opcode)
            handler(vm, argval)


class VM(abc.ABC):
    def __init__(self):
        self.block_stack = [Block(BlockType.Function)]
        self.data_stack = []
        self.statements = []
        self.__variables = {}
        self.__instructions = {}
        self.__ip = 0

    def push(self, tos):
        self.data_stack.append(tos)

    def pop(self):
        return self.data_stack.pop()

    def pushn(self, *args):
        self.data_stack.extend(list(args))

    def popn(self, n):
        retvalues = self.data_stack[-n:]
        self.data_stack[-n:] = []
        return retvalues

    def push_block(self, block):
        self.block_stack.append(block)

    def pop_block(self):
        return self.block_stack.pop()

    def gethandler(self, opcode):
        opname = dis.opname[opcode]
        from . import handlers
        if not hasattr(handlers, opname.lower()):
            raise NotImplementedError(f"{opname} is not implemented yet")
        return getattr(handlers, opname.lower())

    def get_variable(self, name):
        return self.__variables[name]

    def add_statement(self, stmt):
        self.current_block.statements.append(stmt)

    @abc.abstractmethod
    def run(self):
        pass

    @property
    def IP(self):
        return self.__ip

    @IP.setter
    def IP(self, value):
        self.__ip = value

    @property
    def current_instruction(self):
        return self.__instructions[self.IP]

    @property
    def current_block(self):
        return self.block_stack[-1]

    @property
    def instructions(self):
        return self.__instructions


class FunctionVM(VM):
    def __init__(self, func):
        self.func = func
        super().__init__()
        self.__source = None

    def run(self):
        self.setup_variables()
        self.setup_instructions()
        self.IP = 0
        while self.IP <= max(self.__instructions.keys()):
            instruction = self.current_instruction
            opcode = instruction.opcode
            argval = instruction.argval
            offset = instruction.offset
            starts_line = instruction.starts_line
            is_jump_target = instruction.is_jump_target
            if starts_line is not None:
                self.add_source(starts_line)
            print(instruction)
            instruction.run(self)

    def setup_instructions(self):
        for instruction in dis.get_instructions(self.code):
            offset = instruction.offset
            self.__instructions[offset] = InstructionQueue(instruction)

    def setup_variables(self):
        pass

    def resolve_annotations(self):
        """Resolve in-function annotations with regex"""

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

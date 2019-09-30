import abc
import dis
import enum
import inspect
import itertools
from typing import List

from ..session import get_session, new_session
from ..lang.type import *
from ..lang import statement as S, block as B
from . import constant


class BlockType(enum.Enum):
    Empty = enum.auto()
    Class = enum.auto()
    Function = enum.auto()
    Loop = enum.auto()
    Condition = enum.auto()
    Else = enum.auto()
    Try = enum.auto()
    Except = enum.auto()
    Finally = enum.auto()


class LoopType(enum.Enum):
    ForRange = enum.auto()
    While = enum.auto()


class Block:
    def __init__(self, type=None, external=False):
        self.type = type
        self.statements = []
        self.extra_info = {}
        self.external = external

    def add_statement(self, stmt):
        self.statements.append(stmt)

    def realize(self) -> B.Block:
        if self.type == BlockType.Empty:
            return B.EmptyBlock(statements=self.statements)
        elif self.type == BlockType.Condition:
            return B.If(condition=self.extra_info['condition'], statements=self.statements)
        elif self.type == BlockType.Else:
            return B.Else(statements=self.statements)
        elif self.type == BlockType.Loop:
            if self.extra_info['type'] == LoopType.ForRange:
                return B.For(
                    statements=self.statements,
                    variable=self.extra_info['variable'],
                    start=self.extra_info['start'],
                    stop=self.extra_info['stop'],
                    step=self.extra_info['step'],
                )
            elif self.extra_info['type'] == LoopType.While:
                return B.While(condition=self.extra_info['condition'], statements=self.statements)
        elif self.type == BlockType.Function:
            return B.Function(statements=self.statements, **self.extra_info)
        elif self.type == BlockType.Class:
            raise NotImplementedError
        else:
            raise NotImplementedError

    def __enter__(self):
        get_session().push_block(self)

    def __exit__(self, *args):
        if get_session().pop_block() is not self:
            raise RuntimeError("Block stack unbalanced")


class WrappedInstruction:
    def __init__(self, instruction: dis.Instruction):
        self.instruction = instruction
        self.inst_tuple = instruction.opcode, instruction.argval
        self.hooks_before = []
        self.hooks_after = []

    @property
    def offset(self):
        return self.instruction.offset

    @property
    def opcode(self):
        return self.instruction.opcode

    @property
    def opname(self):
        return self.instruction.opname

    @property
    def argval(self):
        return self.instruction.argval

    @property
    def starts_line(self):
        return self.instruction.starts_line

    @property
    def is_jump_target(self):
        return self.instruction.is_jump_target

    def inject_before(self, func, args=(), kwargs={}):
        self.hooks_before.append((func, args, kwargs))

    def inject_after(self, func, args=(), kwargs={}):
        self.hooks_after.append((func, args, kwargs))

    def mute(self):
        self.inst_tuple = constant.NOP, None

    def reset(self):
        self.inst_tuple = self.instruction.opcode, self.instruction.argval

    def run(self, vm):
        self.handle_before_hooks()
        opcode, argval = self.inst_tuple
        handler = vm.gethandler(opcode)
        handler(vm, argval)
        self.handle_after_hooks()

    def handle_before_hooks(self):
        for func, args, kwargs in self.hooks_before:
            func(*args, **kwargs)

    def handle_after_hooks(self):
        for func, args, kwargs in self.hooks_after:
            func(*args, **kwargs)


class VM(abc.ABC):
    def __init__(self, session=None):
        self.data_stack = []
        self.statements = []
        self._variables = {}
        self.__instructions = {}
        self.__ip = 0
        self.__session = session or new_session()

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
        self.session.push_block(block)

    def pop_block(self):
        return self.session.pop_block()

    def gethandler(self, opcode):
        opname = dis.opname[opcode]
        from . import handlers
        if not hasattr(handlers, opname.lower()):
            raise NotImplementedError(f"{opname} is not implemented yet")
        return getattr(handlers, opname.lower())

    def get_variable(self, name):
        return self._variables[name]

    def add_statement(self, stmt):
        self.session.current_block.add_statement(stmt)

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
    def current_instruction(self) -> WrappedInstruction:
        return self.__instructions[self.IP]

    @property
    def instructions(self) -> List[WrappedInstruction]:
        return self.__instructions

    @property
    def session(self):
        return self.__session


class FunctionVM(VM):
    def __init__(self, func, is_method=False, is_constructor=False, session=None):
        self.func = func
        super().__init__(session)
        self.__source = None
        self.__is_method = is_method
        self.__is_constructor = is_constructor

    def run(self):
        self.resolve_signature()
        self.setup_block()
        self.setup_variables()
        self.setup_instructions()
        self.IP = 0
        # first_line = inspect.getsourcelines(self.func)[1]
        while self.IP <= max(self.instructions.keys()):
            instruction = self.current_instruction
            # opcode = instruction.opcode
            # argval = instruction.argval
            # offset = instruction.offset
            # starts_line = instruction.starts_line
            # is_jump_target = instruction.is_jump_target
            # if starts_line is not None:
            #     self.add_source(starts_line - first_line)
            # print(instruction.instruction)
            instruction.run(self)
            self.IP += 2
        for i, block in enumerate(self.session.blocks):
            if isinstance(block, Block):
                self.session.blocks[i] = block.realize()
        return self.block.realize()

    def setup_instructions(self):
        for instruction in dis.get_instructions(self.code):
            offset = instruction.offset
            self.instructions[offset] = WrappedInstruction(instruction)

    def setup_variables(self):
        from ..lang import variable as V
        untyped_variables = set(self.func.__code__.co_varnames)
        local_variables = self.resolve_annotations()
        for type, name in itertools.chain(self.inputs, local_variables):
            untyped_variables.remove(name)
            self._variables[name] = V.Variable(name, type=type)
        if untyped_variables:
            raise TypeError("The following variables are untyped:\n    {}"
                            .format(untyped_variables))
        for _, name in local_variables:
            self.add_statement(S.VariableDeclaration(self.get_variable(name)))

    def setup_block(self):
        block = Block(BlockType.Function, external=True)
        block.extra_info = {
            "name": self.func.__name__,
            "output": self.output,
            "inputs": self.inputs,
            "is_method": self.__is_method,
            "is_constructor": self.__is_constructor,
        }
        self.block = block
        self.push_block(block)

    def get_block(self, name):
        name = name.name
        if name not in self.session.blocks:
            self.session.blocks[name] = Block(BlockType.Empty, external=True)
        return self.session.blocks[name]

    def resolve_annotations(self):
        """Resolve in-function annotations with regex"""
        import re
        pattern = re.compile(r"([a-zA-Z_][a-zA-Z0-9_]*) *: *([a-zA-Z0-9\._]+)")
        source = self.source.split("\n")
        variables = []
        for line in source:
            match = pattern.match(line.strip())
            if match:
                varname = match.group(1)
                annotation = match.group(2)
                type = eval(annotation)
                variables.append((type, varname))
        return variables

    def resolve_signature(self):
        sig = inspect.signature(self.func)
        ret_type = sig.return_annotation
        assert self.__is_constructor == (ret_type == inspect._empty)
        inputs = [(p.annotation, p.name) for p in sig.parameters.values()
                  if not (self.__is_method and p.name == "self")]
        if any(x[0] == inspect._empty for x in inputs):
            raise SyntaxError("All arguments must be annotated")
        self.inputs = inputs
        self.output = ret_type

    def add_source(self, line):
        source = self.source.split("\n")
        self.add_statement(S.SingleLineComment(source[line].strip()))

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

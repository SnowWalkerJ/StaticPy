import dis
import inspect

from . import constant
from .vm import VM
from ..lang import statement as S
from ..lang import expression as E


def pop_top(vm: VM, _):
    item = vm.pop()
    if isinstance(item, E.Expression):
        vm.add_statement(S.from_expression(item))


def rot_two(vm: VM, _):
    a, b = vm.popn(2)
    vm.pushn(b, a)


def rot_three(vm: VM, _):
    a, b, c = vm.popn(3)
    vm.pushn(c, a, b)


def dup_top(vm: VM, _):
    item = vm.pop()
    vm.pushn(item, item)


def dup_top_two(vm: VM, _):
    items = vm.pop(2)
    vm.pushn(*items, *items)


def nop(vm: VM, _):
    pass


def setup_loop(vm: VM, offset: int):
    from .vm import Block, BlockType
    block = Block(BlockType.Loop)
    block.extra_info = {
        "begin_offset": vm.IP + 2,
        "end_offset": offset,
    }
    vm.push_block(block)


def setup_except(vm: VM, _):
    from .vm import Block, BlockType
    block = Block(BlockType.Except)
    vm.push_block(block)


def setup_finally(vm: VM, _):
    from .vm import Block, BlockType
    block = Block(BlockType.Finally)
    vm.push_block(block)


def break_loop(vm: VM, _):
    vm.add_statement(S.Break())


def continue_loop(vm: VM, _):
    vm.add_statement(S.Continue())


def store_name(vm: VM, name):
    # When should this happen?
    raise SyntaxError("Unexpected STORE_NAME")
    var = vm.get_variable(name)
    value = vm.pop()
    vm.add_statement(S.Assign(var, value))


def store_attr(vm: VM, attr):
    value, obj = vm.popn(2)
    vm.add_statement(S.SetAttr(obj, attr, value))


def load_const(vm: VM, value):
    vm.push(E.Const(value))


def load_fast(vm: VM, name):
    vm.push(vm.get_variable(name))


def store_fast(vm: VM, name: str):
    vm.add_statement(S.Assign(vm.get_variable(name), vm.pop()))


def load_name(vm: VM, name: str):
    vm.push(vm.get_name(name))


def load_global(vm: VM, name: str):
    # TODO: needs refactor
    import staticpy as sp
    global_items = {
        "range": range,
        "sp": sp,
    }
    try:
        vm.push(global_items[name])
    except KeyError:
        raise NameError(f"Can't find global item `{name}`")

def load_attr(vm: VM, name):
    vm.push(E.GetAttr(vm.pop(), name))


def compare_op(vm: VM, opname):
    item1, item2 = vm.popn(2)
    vm.push(E.compare_op(opname)(item1, item2))


def build_tuple(vm: VM, n: int):
    vm.push(tuple(vm.popn(n)))


def build_list(vm: VM, n: int):
    vm.push(list(vm.popn(n)))


def build_set(vm: VM, n: int):
    vm.push(set(vm.popn(n)))


def return_value(vm: VM, _):
    vm.add_statement(S.ReturnValue(vm.pop()))


def jump_forward(vm: VM, offset: int):
    pass


def logical_and(vm: VM, _):
    "This is not an instrument"
    a, b = vm.popn(2)
    result = E.LogicalAnd(a, b)
    vm.push(result)


def logical_or(vm: VM, _):
    "This is not an instrument"
    a, b = vm.popn(2)
    result = E.LogicalOr(a, b)
    vm.push(result)


def jump_if_false_or_pop(vm: VM, offset: int):
    "This is used as `a and b`"
    target = vm.instructions[offset]
    target.inject_before(logical_and, (vm, None))


def jump_if_true_or_pop(vm: VM, offset: int):
    "This is used as `a or b`"
    target = vm.instructions[offset]
    target.inject_before(logical_or, (vm, None))


def jump_absolute(vm: VM, offset: int):
    from .vm import BlockType, Block
    def _continue_statement():
        if offset != vm.session.current_block.extra_info["begin_offset"]:
            raise SyntaxError("Unexpected JUMP_ABSOLUTE target")
        if vm.instructions[offset+2].opcode == constant.POP_BLOCK:
            # end of loop
            return
        else:
            vm.add_statement(S.Continue())

    def _else_statement():
        # JUMP_ABSOLUTE at the end of IF
        vm.instructions[vm.IP+2].inject_before(lambda: vm.push_block(Block(BlockType.Else)), ())
        vm.instructions[offset-2].inject_after(pop_block, (vm, None))

    current_block = vm.session.current_block
    if current_block.type == BlockType.Loop:
        _continue_statement()
    elif current_block.type == BlockType.Condition and vm.IP == current_block.extra_info['end_offset']:
        _else_statement()
    else:
        raise SyntaxError("Unexpected JUMP_ABSOLUTE target")


def pop_jump_if_false(vm: VM, offset: int):
    """
    POP_JUMP_IF_FALSE can be used in either an "if" statement
    or a "while" statement.

    The circumstances of a "while" statement meets the following
    requirements:

    1. there is a SETUP_LOOP before but the loop type is not determined
    2. target of the jump is a POP_BLOCK statement
    3. right before POP_BLOCK there is a JUMP_ABSOLUTE targeting
    after SETUP_LOOP
    """
    from .vm import Block, BlockType, LoopType
    condition = vm.pop()
    target = vm.instructions[offset]

    def _if_statement():
        block = Block(BlockType.Condition)
        block.extra_info = {
            "condition": condition,
            "begin_offset": vm.IP + 2,
            "end_offset": offset - 2,
        }
        if offset > vm.IP:
            vm.instructions[offset - 2].inject_after(pop_block, (vm, None))
        else:
            if vm.session.current_block.type == BlockType and \
                    offset == vm.session.current_block.extra_info['begin_offset']:
                vm.current_instrument.inject_after(continue_loop, (vm, None))
                vm.curent_instrument.inject_after(pop_block, (vm, None))
            else:
                raise SyntaxError("Unexected JUMP target")
        vm.push_block(block)

    def _while_statement():
        block.extra_info.update({
            "type": LoopType.While,
            "condition": condition,
        })
        vm.instructions[offset - 2].mute()   # mute the last abundant JUMP_ABSOLUTE

    block = vm.session.current_block
    cond1 = block.type == BlockType.Loop and not block.extra_info.get('type')
    cond2 = target.opcode == constant.POP_BLOCK
    cond3 = vm.instructions[offset - 2].opcode == constant.JUMP_ABSOLUTE
    if cond1 and cond2 and cond3:
        _while_statement()
    else:
        _if_statement()


def pop_jump_if_true(vm: VM, _):
    raise NotImplementedError


def get_iter(vm: VM, _):
    item = vm.pop()
    if item.func != range:
        raise NotImplementedError("Currently only for-range is supported")
    args = item.args
    if len(args) == 1:
        start, stop, step = 0, args[0], 1
    elif len(args) == 2:
        start, stop, step = args[0], args[1], 1
    else:
        start, stop, step = args
    vm.push(("range", start, stop, step))


def for_iter(vm: VM, offset: int):
    from .vm import LoopType
    _, start, stop, step = vm.pop()
    vm.IP += 2
    if vm.current_instruction.opcode != constant.STORE_FAST:
        raise SyntaxError("Can't recognize opcode {opcode}({opname}) after FOR_ITER".format(
                          opcode=vm.current_instruction.opcode, opname=vm.current_instruction.opname))
    iter_var = vm.get_variable(vm.current_instruction.argval)
    vm.session.current_block.extra_info.update({
        "type": LoopType.ForRange,
        "start": start,
        "stop": stop,
        "step": step,
        "variable": iter_var,
    })
    vm.instructions[offset - 2].mute()   # mute the last abundant JUMP_ABSOLUTE


def call_function(vm: VM, nargs: int):
    args = vm.popn(nargs)
    func = vm.pop()
    vm.push(E.CallFunction(func, args))


def store_subscr(vm: VM, _):
    value, index, obj = vm.popn(3)
    vm.add_statement(S.SetItem(obj, index, value))


def pop_block(vm: VM, _):
    block = vm.pop_block()
    if not block.external:
        vm.add_statement(S.BlockStatement(block.realize()))


def import_star(vm: VM, _):
    name = vm.pop()
    vm.add_statement(S.UsingNamespace(name))


def setup_with(vm: VM, _):
    name = vm.pop()
    block = self.get_block(name)
    vm.push(None)        # return value of __enter__
    self.push_block(block)


def with_cleanup_start(vm: VM, _):
    pass


def with_cleanup_finish(vm: VM, _):
    pass


def end_finally(vm: VM, _):
    pass


def unary_operation(expression):
    def fn(vm: VM, _):
        item = vm.pop()
        item = expression(item)
        vm.push(item)
    return fn


def binary_operation(expression):
    def fn(vm: VM, _):
        item1, item2 = vm.popn(2)
        result = expression(item1, item2)
        vm.push(result)
    return fn


def inplace_operation(expression):
    def fn(vm: VM, _):
        item1, item2 = vm.popn(2)
        result = expression(item1, item2)
        vm.add_statement(result)
        store_inst = vm.instructions[vm.IP+2]
        if store_inst.opcode != constant.STORE_FAST:
            raise RuntimeError("Expect STORE_FAST right after inplace operation")
        store_inst.mute()
    return fn


def ternary_operation(expression):
    def fn(vm: VM, _):
        item1, item2, item3 = vm.popn(3)
        result = expression(item1, item2, item3)
        vm.push(result)
    return fn


def not_implemented(vm: VM, _):
    raise NotImplementedError


unary_positive = unary_operation(E.UnaryPositive)
unary_negative = unary_operation(E.UnaryNegative)
unary_not = unary_operation(E.UnaryNot)
unary_invert = unary_operation(E.UnaryInvert)
binary_matrix_multiply = not_implemented
inplace_matrix_multiply = not_implemented
binary_power = not_implemented
binary_multiply = binary_operation(E.BinaryMultiply)
binary_modulo = binary_operation(E.BinaryModulo)
binary_add = binary_operation(E.BinaryAdd)
binary_subtract = binary_operation(E.BinarySubtract)
binary_subscr = binary_operation(E.GetItem)
binary_floor_divide = binary_operation(E.BinaryDivide)
binary_true_divide = binary_operation(E.BinaryDivide)
binary_power = not_implemented
get_aiter = not_implemented
get_anext = not_implemented
before_async_with = not_implemented
inplace_add = inplace_operation(S.InplaceAdd)
inplace_subtract = inplace_operation(S.InplaceSubtract)
inplace_multiply = inplace_operation(S.InplaceMultiply)
inplace_modulo = inplace_operation(S.InplaceModulo)
store_subscr = ternary_operation(S.SetItem)
delete_subscr = not_implemented
binary_lshift = binary_operation(E.BinaryLShift)
binary_rshift = binary_operation(E.BinaryRShift)
binary_and = binary_operation(E.BinaryAnd)
binary_xor = binary_operation(E.BinaryXor)
binary_or = binary_operation(E.BinaryOr)
inplace_power = not_implemented
get_yield_from_iter = not_implemented
print_expr = not_implemented
load_build_class = not_implemented
yield_from = not_implemented
get_awaitable = not_implemented
inplace_lshift = inplace_operation(S.InplaceLShift)
inplace_rshift = inplace_operation(S.InplaceRShift)
inplace_and = inplace_operation(S.InplaceAnd)
inplace_xor = inplace_operation(S.InplaceXor)
inplace_or = inplace_operation(S.InplaceOr)
setup_annotations = not_implemented
yield_value = not_implemented
pop_except = not_implemented
delete_name = not_implemented
unpack_sequence = not_implemented
unpack_ex = not_implemented
delete_attr = not_implemented
store_global = not_implemented
delete_global = not_implemented
build_map = not_implemented
import_name = not_implemented
import_from = not_implemented
delete_fast = not_implemented
raise_varargs = not_implemented
make_function = not_implemented
build_slice = not_implemented
load_closure = not_implemented
load_deref = not_implemented
store_deref = not_implemented
delete_deref = not_implemented
call_function_kw = not_implemented
call_function_ex = not_implemented
list_append = not_implemented
set_add = not_implemented
map_add = not_implemented
load_classderef = not_implemented
extended_arg = not_implemented
build_list_unpack = not_implemented

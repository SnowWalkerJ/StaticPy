import dis
import inspect

from . import constant
from .vm import VM
from .. import statement as S
from .. import expression as E


def pop_top(vm: VM, _):
    item = vm.pop()
    if isinstance(item, E.Expression):
        vm.add_statement(S.from_expression(item))


def rot_two(vm: VM, _):
    a, b = vm.popn(2)
    vm.pushn(b, a)


def ROT_THREE(vm: VM, _):
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


def load_name(vm: VM, name):
    vm.push(vm.get_name(name))


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


def jump_if_false_or_pop(vm: VM, offset: int):
    "This is used as `a and b`"
    target = vm.instructions[offset]
    target.inject_before(binary_and, (vm, None))


def jump_if_true_or_pop(vm: VM, offset: int):
    "This is used as `a or b`"
    target = vm.instructions[offset]
    target.inject_before(binary_or, (vm, None))


def jump_absolute(vm: VM, offset: int):
    from .vm import BlockType
    if vm.session.current_block.type == BlockType.Loop:
        # NOTE: This assumes a JUMP_ABSOLUTE inside Loop only aims at start of loop
        if vm.instructions[offset+2].opcode == constant.POP_BLOCK:
            # end of loop
            return
        else:
            vm.add_statement(S.Continue())
    elif vm.session.current_block.type == BlockType.Condition:
        # TODO: JUMP_ABSOLUTE inside if
        raise NotImplementedError


def pop_jump_if_false(vm: VM, offset: int):
    from .vm import Block, BlockType
    condition = vm.pop()
    block = Block(BlockType.Condition)
    block.extra_info = {
        "condition": condition,
    }
    vm.push_block(block)
    if offset > vm.IP:
        target = vm.instructions[offset]
        target.inject_before(pop_block, (vm, None))
    else:
        # TODO: handle this situation
        raise NotImplementedError


def pop_jump_if_true(vm: VM, _):
    pass


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


def for_iter(vm: VM, n: int):
    _, start, stop, step = vm.pop()
    vm.IP += 2
    if vm.current_instruction.opcode != constant.STORE_FAST:
        raise SyntaxError("Can't recognize opcode {opcode}({opname}) after FOR_ITER".format(
                          opcode=vm.current_instruction.opcode, opname=vm.current_instruction.opname))
    iter_var = vm.get_variable(vm.current_instruction.argval)
    vm.session.current_block.extra_info = {
        "start": start,
        "stop": stop,
        "step": step,
        "variable": iter_var,
    }


def call_function(vm: VM, nargs: int):
    args = vm.popn(nargs)
    func = vm.pop()
    vm.push(E.CallFunction(func, args))


def store_subscr(vm: VM, _):
    value, index, obj = vm.popn(3)
    vm.add_statement(S.SetItem(obj, index, value))


def pop_block(vm: VM, _):
    block = vm.pop_block()
    vm.add_statement(S.BlockStatement(block))


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
        vm.push(result)
        store_inst = vm.instructions[IP+2]
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
inplace_and = not_implemented
inplace_xor = not_implemented
inplace_or = not_implemented
with_cleanup_start = not_implemented
with_cleanup_stop = not_implemented
import_star = not_implemented
setup_annotations = not_implemented
yield_value = not_implemented
end_finally = not_implemented
pop_except = not_implemented
delete_name = not_implemented
unpack_sequence = not_implemented
for_iter = not_implemented
unpack_ex = not_implemented
delete_attr = not_implemented
store_global = not_implemented
delete_global = not_implemented
build_map = not_implemented
import_name = not_implemented
import_from = not_implemented
load_global = not_implemented
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
setup_with = not_implemented
list_append = not_implemented
set_add = not_implemented
map_add = not_implemented
load_classderef = not_implemented
extended_arg = not_implemented
build_list_unpack = not_implemented

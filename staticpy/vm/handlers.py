import dis

from . import constant
from .vm import VM
from .. import statement as S
from .. import expression as E


def pop_top(vm: VM, _):
    vm.pop()


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


def setup_loop(vm: VM, _):
    raise NotImplementedError


def setup_except(vm: VM, _):
    raise NotImplementedError


def setup_finally(vm: VM, _):
    raise NotImplementedError


def break_loop(vm: VM, _):
    raise NotImplementedError


def continue_loop(vm: VM, _):
    raise NotImplementedError


def store_name(vm: VM, name):
    raise NotImplementedError


def store_attr(vm: VM, _):
    raise NotImplementedError


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
    vm.push(E.compare_op(dis.cmp_op[opname])(item1, item2))


def build_tuple(vm: VM, n: int):
    vm.push(vm.popn(n))


def build_list(vm: VM, n: int):
    vm.push(list(vm.popn(n)))


def build_set(vm: VM, n: int):
    vm.push(set(vm.popn(n)))


def return_value(vm: VM, _):
    raise NotImplementedError


def jump_forward(vm: VM, offset: int):
    pass


def jump_if_false_or_pop(vm: VM, offset: int):
    pass


def jump_if_true_or_pop(vm: VM, offset: int):
    pass


def jump_absolute(vm: VM, offset: int):
    pass


def pop_jump_if_false(vm: VM, _):
    pass


def pop_jump_if_true(vm: VM, _):
    pass


def call_function(vm: VM, nargs: int):
    args = vm.popn(nargs)
    func = vm.pop()
    vm.push(E.CallFunction(func, args))


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
binary_subscr = binary_operation(E.BinarySubscr)
binary_floor_divide = binary_operation(E.BinaryFloorDivide)
binary_true_divide = binary_operation(E.BinaryTrueDivide)
binary_power = binary_operation(E.BinaryPower)
get_aiter = not_implemented
get_anext = not_implemented
before_async_with = not_implemented
inplace_add = binary_operation(E.InplaceAdd)
inplace_subtract = binary_operation(E.InplaceSubtract)
inplace_multiply = binary_operation(E.InplaceMultiply)
inplace_modulo = binary_operation(E.InplaceModulo)
store_subscr = ternary_operation(E.StoreSubscr)
delete_subscr = not_implemented
binary_lshift = binary_operation(E.BinaryLShift)
binary_rshift = binary_operation(E.BinaryRShift)
binary_and = binary_operation(E.BinaryAnd)
binary_xor = binary_operation(E.BinaryXor)
binary_or = binary_operation(E.BinaryOr)
inplace_power = not_implemented
get_iter = not_implemented
get_yield_from_iter = not_implemented
print_expr = not_implemented
load_build_class = not_implemented
yield_from = not_implemented
get_awaitable = not_implemented
inplace_lshift = binary_operation(E.InplaceLShift)
inplace_rshift = binary_operation(E.InplaceRShift)
inplace_and = binary_operation(E.InplaceAnd)
inplace_xor = binary_operation(E.InplaceXor)
inplace_or = binary_operation(E.InplaceOr)
with_cleanup_start = not_implemented
with_cleanup_stop = not_implemented
import_star = not_implemented
setup_annotations = not_implemented
yield_value = not_implemented
pop_block = not_implemented
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

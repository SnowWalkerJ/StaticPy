import math
from ..lang import expression as E
from ..lang.common import require_header
from ..common.phase import LibFunction


def math_function(name):
    return LibFunction("<cmath>", getattr(math, name), name, "std")


cos = math_function("cos")

sin = math_function("sin")

tan = math_function("tan")

acos = math_function("acos")

asin = math_function("asin")

atan = math_function("atan")

cosh = math_function("cosh")

sinh = math_function("sinh")

tanh = math_function("tanh")

acosh = math_function("acosh")

asinh = math_function("asinh")

atanh = math_function("atanh")

exp = math_function("exp")

expm1 = math_function("expm1")

log = math_function("log")

log10 = math_function("log10")

log2 = math_function("log2")

log1p = math_function("log1p")

pow = math_function("pow")

sqrt = math_function("sqrt")

ceil = math_function("ceil")

floor = math_function("floor")

fmax = LibFunction("<cmath>", max, "fmax", "std")

fmin = LibFunction("<cmath>", min, "fmin", "std")

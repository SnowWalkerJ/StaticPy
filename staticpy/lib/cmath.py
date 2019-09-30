from ..lang import expression as E
from ..lang.common import require_header


@require_header(["<cmath>"])
def cos(value):
    return E.CallFunction('cos', (value, ))


@require_header(["<cmath>"])
def sin(value):
    return E.CallFunction('sin', (value, ))


@require_header(["<cmath>"])
def tan(value):
    return E.CallFunction('tan', (value, ))


@require_header(["<cmath>"])
def acos(value):
    return E.CallFunction('acos', (value, ))


@require_header(["<cmath>"])
def asin(value):
    return E.CallFunction('asin', (value, ))


@require_header(["<cmath>"])
def atan(value):
    return E.CallFunction('atan', (value, ))


@require_header(["<cmath>"])
def atan2(value1, value2):
    return E.CallFunction('atan2', (value1, value2))


@require_header(["<cmath>"])
def cosh(value):
    return E.CallFunction('cosh', (value, ))


@require_header(["<cmath>"])
def sinh(value):
    return E.CallFunction('sinh', (value, ))


@require_header(["<cmath>"])
def tanh(value):
    return E.CallFunction('tanh', (value, ))


@require_header(["<cmath>"])
def acosh(value):
    return E.CallFunction('acosh', (value, ))


@require_header(["<cmath>"])
def asinh(value):
    return E.CallFunction('asinh', (value, ))


@require_header(["<cmath>"])
def atanh(value):
    return E.CallFunction('atanh', (value, ))


@require_header(["<cmath>"])
def exp(value):
    return E.CallFunction('exp', (value, ))


@require_header(["<cmath>"])
def exp2(value):
    return E.CallFunction('exp2', (value, ))


@require_header(["<cmath>"])
def expm1(value):
    return E.CallFunction('expm1', (value, ))


@require_header(["<cmath>"])
def log(value):
    return E.CallFunction('log', (value, ))


@require_header(["<cmath>"])
def log10(value):
    return E.CallFunction('log10', (value, ))


@require_header(["<cmath>"])
def log2(value):
    return E.CallFunction('log2', (value, ))


@require_header(["<cmath>"])
def log1p(value):
    return E.CallFunction('log1p', (value, ))


@require_header(["<cmath>"])
def pow(base, exponent):
    return E.CallFunction('pow', (base, exponent))


@require_header(["<cmath>"])
def sqrt(value):
    return E.CallFunction('sqrt', (value, ))


@require_header(["<cmath>"])
def ceil(value):
    return E.CallFunction('ceil', (value, ))


@require_header(["<cmath>"])
def floor(value):
    return E.CallFunction('floor', (value, ))


@require_header(["<cmath>"])
def fmax(a, b):
    return E.CallFunction('fmax', (a, b))


@require_header(["<cmath>"])
def fmin(a, b):
    return E.CallFunction('fmin', (a, b))

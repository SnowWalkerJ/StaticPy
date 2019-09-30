from ..lang import variable as V, statement as S
from ..session import get_session
from ..lang.common import require_header


@require_header(['<iostream>'])
def cprint(*args, **kwargs):
    expr = cout
    init = True
    for obj in args:
        if not init:
            expr = expr << ", "
        expr = expr << obj
        init = False
    for name, value in kwargs.items():
        if not init:
            expr = expr << ", "
        expr = expr << (name + " = ") << value
        init = False

    expr = expr << endl
    return expr


cin = V.Name('std::cin')
cout = V.Name('std::cout')
cerr = V.Name('std::cerr')
endl = V.Name('std::endl')

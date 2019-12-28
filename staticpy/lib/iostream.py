from ..lang import expression as E, statement as S
from ..session import get_session
from ..lang.common import require_header
from ..common.phase import LibFunction


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


cprint = LibFunction("<iostream>", print, cprint)


cin = E.ScopeAnalysis("std", "cin")
cout = E.ScopeAnalysis("std", "cout")
cerr = E.ScopeAnalysis("std", "cerr")
endl = E.ScopeAnalysis("std", "endl")

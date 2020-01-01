import sys

from ..lang import expression as E, statement as S
from ..session import get_session
from ..lang.common import require_header
from ..lang.common.func import get_block_or_create
from ..lang import macro as M
from ..common.phase import TwoPhaseFunction, LibObject


class cprint(TwoPhaseFunction):
    def normal(self, *args, **kwargs):
        args = list(map(str, args))
        for name, value in kwargs.items():
            args.append(f"{name} = {value}")
        print(", ".join(args))

    def building(self, *args, **kwargs):
        with get_block_or_create('header'):
            M.include("<iostream>")
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


class IOStream:
    def __init__(self, file):
        self._stream = file

    def __lshift__(self, other):
        print(other, file=self._stream, end="")
        return self

    def __rshift__(self, other):
        raise NotImplementedError("`>>` operator for istream object is not implemented in Python")


def iostream_function(name, obj):
    return LibObject("<iostream>", lambda: obj, name, "std")


cin = iostream_function("cin", IOStream(sys.stdin))
cout = iostream_function("cout", IOStream(sys.stdout))
cerr = iostream_function("cerr", IOStream(sys.stderr))
endl = iostream_function("endl", "\n")

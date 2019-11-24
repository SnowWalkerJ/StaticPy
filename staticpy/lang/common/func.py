import functools
import typing

from ...session import get_session
from .. import statement as S


def auto_add(wrapped):

    @functools.wraps(wrapped)
    def fn(*args, **kwargs):
        from .. import block as B
        stmt = obj = wrapped(*args, **kwargs)
        if isinstance(stmt, B.Block):
            stmt = S.BlockStatement(stmt)
        get_session().current_block.add_statement(stmt)
        return obj
    return fn


def require_header(headers: typing.List[str]):
    from .. import macro as M

    def decorator(wrapped):

        @functools.wraps(wrapped)
        def func(*args, **kwargs):
            with get_block_or_create('header'):
                for header in headers:
                    M.include(header)
            return wrapped(*args, **kwargs)
        return func
    return decorator


def get_block_or_create(name: str):
    from .. import block as B
    sess = get_session()
    if name not in sess.blocks:
        sess.blocks[name] = B.EmptyBlock()
    return sess.blocks[name]

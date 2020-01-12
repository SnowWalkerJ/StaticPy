class Session:
    def __init__(self):
        self.blocks = {}
        self.block_stack = []
        self.includes = set()
        self.definitions = set()

    @property
    def current_block(self):
        return self.block_stack[-1]

    def push_block(self, block):
        self.block_stack.append(block)

    def pop_block(self):
        return self.block_stack.pop()

    def add_include(self, filename):
        self.includes.add(filename)

    def add_definition(self, obj):
        self.definitions.add(obj)

    def finalize(self):
        from .lang.common.func import get_block_or_create
        from .lang import macro as M, statement as S
        with self:
            header = get_block_or_create("header")
            with header:
                for filename in self.includes:
                    M.include(filename)
            for obj in self.definitions:
                block = obj._translate(self)
                header.add_statement(S.BlockStatement(block))

    def __enter__(self):
        global _sessions
        _sessions.append(self)
        return self

    def __exit__(self, *args):
        global _sessions
        _sessions.pop()


_sessions = []


def get_session() -> Session:
    global _sessions
    if not _sessions:
        _sessions.append(Session())
    return _sessions[-1]


def new_session() -> Session:
    return Session()

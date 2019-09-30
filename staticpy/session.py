class Session:
    def __init__(self):
        self.blocks = {}
        self.block_stack = []
        self.functions = []
        self.classes = []

    @property
    def current_block(self):
        return self.block_stack[-1]

    def push_block(self, block):
        self.block_stack.append(block)

    def pop_block(self):
        return self.block_stack.pop()

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
    return _sessions[-1]


def new_session() -> Session:
    return Session()

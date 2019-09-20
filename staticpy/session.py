class Session:
    def __init__(self):
        self.blocks = []
        self.pure = True

    def push_block(self, block):
        self.blocks.append(block)

    def pop_block(self):
        return self.blocks.pop()

    def __enter__(self):
        global __sessions
        __sessions.append(self)
        return self

    def __exit__(self, *args):
        global __sessions
        __sessions.pop()


__sessions = []


def get_session():
    global __sessions
    return __sessions[-1]

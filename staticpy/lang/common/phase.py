import abc
from contextlib import contextmanager
__building = 0


def is_building():
    return __building


@contextmanager
def set_building():
    global __building
    __building += 1
    yield
    __building -= 1


class TwoPhaseFunction(abc.ABC):
    def __call__(self, *args, **kwargs):
        if is_building():
            return self.normal(*args, **kwargs)
        else:
            return self.building(*args, **kwargs)

    @abc.abstractmethod
    def normal(self, *args, **kwargs):
        pass

    @abc.abstractmethod
    def building(self, *args, **kwargs):
        pass


class overload(TwoPhaseFunction):
    def normal(self, func):
        pass

    def building(self, func):
        return func

import inspect

from ..lib import cmath, iostream


modules = [cmath, iostream]
objects = {}


def search_builtin(name: str):
    if name in objects:
        return objects[name]
    for module in modules:
        item = getattr(module, name)
        if item is not None:
            return item
    raise NameError

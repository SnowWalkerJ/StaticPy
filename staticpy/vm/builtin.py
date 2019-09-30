import inspect

from ..lang import variable as V
from ..lib import cmath, iostream


modules = [cmath, iostream]
objects = {
    "range": V.Name("range"),
    "print": iostream.cprint,
}


def search_builtin(name: str):
    if name in objects:
        return objects[name]
    for module in modules:
        item = getattr(module, name, None)
        if item is not None:
            return item
    raise NameError

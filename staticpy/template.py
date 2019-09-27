from abc import ABC, abstractmethod

import jinja2

from ..macro import include


class Template(ABC):
    @abstractmethod
    def render(self, blocks, libname):
        pass

    @classmethod
    def get_template(cls):
        origin_cls = cls
        while cls is not Template:
            if cls.__doc__:
                return cls.__doc__
            else:
                cls = cls.__base__
        raise ValueError(f"Tempalte `{origin_cls}` doesn't have doc")


class CppTemplate(Template):
    """#define _likely(x) __builtin_expect((x), 1)
#define _unlikely(x) __builtin_expect((x), 0)
{{header}}

{{global}}

{{footer}}"""

    def render(self, blocks, libname):
        template = jinja2.Template(self.get_template())
        params = {}
        for name, (block, level) in blocks.items():
            params[name] = "\n".join(["  " * level + line for line in block.translate()])
        return template.render(**params)

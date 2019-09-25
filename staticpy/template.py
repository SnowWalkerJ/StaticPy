from abc import ABC, abstractmethod

import jinja2

from ..macro import include


class Template(ABC):
    def __init__(self, compiler):
        self.compiler = compiler

    def setup_before(self, compiler, session):
        pass

    def setup_after(self, compiler, session):
        pass

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
    def setup_before(self, compiler, session):
        compiler.register_block("header", 0)
        compiler.register_block("global", 0)
        compiler.register_block("footer", 0)

    def setup_after(self, compiler, session):
        for header in session.headers:
            compiler.get_block("header").add_statement(include(header))
        for function in session.functions:
            compiler.get_block("global").add_block(function)
        for cls in session.classes:
            compiler.get_block("global").add_block(cls)

    def render(self, blocks, libname):
        template = jinja2.Template(self.get_template())
        params = {}
        for name, (block, level) in blocks.items():
            params[name] = "\n".join(["  " * level + line for line in block.translate()])
        return template.render(**params)

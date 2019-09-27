from abc import ABC, abstractmethod
import importlib
from enum import Enum
import types
from inspect import getdoc, getmembers

from .lang import (
    block as B,
    statement as S,
    expression as E,
    macro as M,
    type as T,
    variable as V,
)
from .session import get_session


class PrivilegeEnum(Enum):
    ReadOnly = 0
    Writable = 1


class PyBindModuleScope(B.Scope):
    def __init__(self, name, parent=None):
        super().__init__(parent)
        self.name = name

    def prefix(self):
        return f"PYBIND11_MODULE({self.name}, m) {{"


class PyBindModule:
    def __init__(self, module):
        self.module = module

    def setup(self, session):
        with session.get_block("header"):
            with M.ifdefBM("PYBIND"):
                M.include("<pybind11/pybind11.h>")
                S.statement("namespace py = pybind11;")
        with session.get_block("footer"):
            self.define()

    def define(self):
        m = V.Name("m")
        with M.ifdefBM("PYBIND"):
            block = PyBindModuleScope(self.module.__name__)
            with block:
                if self.doc:
                    S.assign(V.Name("m.doc()"), self.doc)
                for name, value in getmembers(self.module):
                    value.bind(m)
            get_session().current_block.add_statement(S.BlockStatement(block))

    @property
    def doc(self):
        return getdoc(self.module)


class BindObject(ABC):
    def __init__(self, obj):
        self.obj = obj
        self.name = obj.__name__

    @property
    def doc(self):
        return getdoc(self.obj) or ""

    @abstractmethod
    def bind(self, parent, namespace=None):
        pass

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
from .lang.common import get_block_or_create
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

    def translate(self):
        return super().translate()


class BindObject(ABC):
    def __init__(self, obj):
        self.obj = obj
        self.name = obj.__name__

    @property
    def doc(self):
        return getdoc(self.obj) or ""

    def setup(self, session):
        with session:
            with get_block_or_create("header"):
                with M.ifdefBM("PYBIND"):
                    M.include("<pybind11/pybind11.h>")
                    S.statement("namespace py = pybind11;")
            with get_block_or_create("footer"):
                self.define()

    @abstractmethod
    def define(self):
        pass


class PyBindModule(BindObject):
    def __init__(self, module):
        super().__init__(module)

    def define(self):
        m = V.Name("m")
        with M.ifdefBM("PYBIND"):
            block = PyBindModuleScope(self.obj.__name__)
            with block:
                if self.doc:
                    S.assign(V.Name("m.doc()"), self.doc)
                for _, value in getmembers(self.obj):
                    if isinstance(value, BindObject):
                        value.bind(m)
            get_session().current_block.add_statement(S.BlockStatement(block))


class PyBindFunction(BindObject):
    def __init__(self, name, inputs, output, is_method=False, is_constructor=False, doc=""):
        self.name = name
        self.inputs = inputs
        self.output = output
        self.is_method = is_method
        self.is_constructor = is_constructor
        self._doc = doc

    def define(self):
        m = V.Name("m")
        with M.ifdefBM("PYBIND"):
            block = PyBindModuleScope(self.obj.__name__)
            with block:
                if self.doc:
                    S.assign(V.Name("m.doc()"), self.doc)
                self.bind(m)
            get_session().current_block.add_statement(S.BlockStatement(block))

    def bind(self, parent, namespace=None):
        if self.is_constructor:
            template = E.ScopeAnalysis(V.Name("py"), V.Name("init"))
            args = (V.Name(str(type)) for _, type in self.inputs)
            args = (E.CallFunction(E.TemplateInstantiate(template, args), ()), )
        else:
            args = (self.name, self.address(namespace), self.doc)
        S.as_statement(E.CallFunction(E.GetAttr(parent, "def"), args))

    def address(self, namespace=None):
        if namespace:
            name = E.ScopeAnalysis(V.Name(namespace), V.Name(self.name))
        else:
            name = self.name
        return E.AddressOf(V.Name(name))

    @property
    def doc(self):
        return self._doc


class PyBindFunctionGroup(PyBindFunction):
    def __init__(self, name, functions, doc=""):
        self.name = name
        self._doc = doc
        self.functions = functions

    def define(self):
        m = V.Name("m")
        with M.ifdefBM("PYBIND"):
            block = PyBindModuleScope(self.name)
            with block:
                if self.doc:
                    S.assign(V.Name("m.doc()"), self.doc)
                for func in self.functions:
                    func.bind(m)
            get_session().current_block.add_statement(S.BlockStatement(block))

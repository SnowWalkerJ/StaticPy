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
from .util.string import function_pointer_signature
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
    def __init__(self, name, obj):
        self.obj = obj
        self.name = name

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

    def _wrap_function(self, block):
        doc = block.doc
        wrapped_inputs = [(T.ReferenceType(t) if isinstance(t, T.ArrayType) else t, n) for (t, n) in block.inputs]
        # if any, wrap the array types
        if any(isinstance(type, T.ArrayType) for type, name in block.inputs):
            wrapped_inputs = []
            params = []
            wrapped_func = B.EmptyBlock()
            auto_t = T.OtherType(V.Name("auto"))
            with wrapped_func:
                for t, n in block.inputs:
                    if isinstance(t, T.ArrayType):
                        buffer_t = T.OtherType(E.ScopeAnalysis(V.Name("py"), V.Name("buffer")))
                        wrapped_inputs.append((buffer_t, n))
                        v_in = V.variable(n, buffer_t)
                        v_out = V.variable("_" + n, t)
                        buffer_info = V.variable(f"buffer_info_{n}", auto_t)
                        S.declare(buffer_info, E.CallFunction(E.GetAttr(v_in, "request"), ()))
                        S.declare(v_out, E.CallFunction(t.cname(), (buffer_info, )))
                        params.append(v_out)
                    else:
                        wrapped_inputs.append((t, n))
                        params.append(V.variable(n, t))
                S.returns(E.CallFunction(block.name, tuple(params)))
            wrapped_func = B.Function(block.name, wrapped_inputs, block.output, wrapped_func.statements, block.doc)
            m = M.IfDefMacro("PYBIND")
            m.add_statement(S.BlockStatement(wrapped_func))
            block.parent.add_statement(S.BlockStatement(m))
            inputs = wrapped_inputs
        else:
            inputs = [(t.wrapped(), n) for t, n in block.inputs]
        return inputs


class PyBindModule(BindObject):
    def __init__(self, name, module):
        super().__init__(name, module)

    def define(self):
        m = V.Name("m")
        with M.ifdefBM("PYBIND"):
            block = PyBindModuleScope(self.name)
            with block:
                if self.doc:
                    S.assign(V.Name("m.doc()"), self.doc)
                for stmt in self.obj.statements:
                    if isinstance(stmt, S.BlockStatement) and isinstance(stmt.block, B.Function):
                        PyBindFunction(stmt.block.name, stmt.block).bind(m)
            get_session().current_block.add_statement(S.BlockStatement(block))


class PyBindFunction(BindObject):
    def __init__(self, name, func_block, is_method=False, is_constructor=False):
        self.block = func_block
        self.name = func_block.name
        self.is_method = is_method
        self.is_constructor = is_constructor
        self._doc = func_block.doc

    def define(self):
        m = V.Name("m")
        with M.ifdefBM("PYBIND"):
            block = PyBindModuleScope(self.name)
            with block:
                if self.doc:
                    S.assign(V.Name("m.doc()"), self.doc)
                self.bind(m)
            get_session().current_block.add_statement(S.BlockStatement(block))

    def bind(self, parent, namespace=None):
        inputs = self._wrap_function(self.block)
        if self.is_constructor:
            template = E.ScopeAnalysis(V.Name("py"), V.Name("init"))
            args = (V.Name(str(type)) for _, type in inputs)
            args = (E.CallFunction(E.TemplateInstantiate(template, args), ()), )
        else:
            args = (self.name, E.Cast(self.address(namespace), V.Name(function_pointer_signature(inputs, self.block.output))), self.doc)
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


import ast
import collections
import functools
import os
import sys

from .session import get_session, new_session
from .lang import (
    type as T,
    variable as V,
    expression as E,
    statement as S,
    block as B,
    macro as M,
)


class ContextStack:
    annotation_map = {
        "int": T.Int,
        "long": T.Long,
        "float": T.Float,
        "double": T.Double,
        "str": T.String,
        "Int": T.Int,
        "Long": T.Long,
        "Float": T.Float,
        "Double": T.Double,
        "String": T.String,
        "T": T,
    }

    def __init__(self, globals={}):
        globals = globals.copy()
        globals.update(self.annotation_map)
        self.stack = [(globals, {})]

    def push(self, env=None):
        if env is None:
            env = {}
        self.stack.append((env, {}))

    def pop(self):
        self.stack.pop()

    def __getitem__(self, key):
        return self._find(key, self.stack)[0]

    def __setitem__(self, key, value):
        try:
            _, env = self._find(key, self.stack)
        except KeyError:
            env = self.stack[-1][0]
        env[key] = value

    def _find(self, key, stack):
        if not stack:
            raise KeyError()
        env, cache = stack[-1]
        if key not in cache:
            if key in env:
                cache[key] = (env[key], env)
            else:
                cache[key] = self._find(key, stack[:-1])
        return cache[key]

    def __enter__(self):
        self.push()

    def __exit__(self, *args):
        self.pop()


class BaseTranslator:
    def __init__(self, ctx={}, session=None):
        self.ctx = ContextStack(ctx)
        self.sess = session
        self.source = None
        self.err_handled = False

    def translate(self, source):
        lines = source.split("\n")
        indents = min(len(line) - len(line.lstrip()) for line in lines if line.lstrip())
        self.source = "\n".join(line[indents:] for line in lines)
        self.sess = self.sess or new_session()
        self.err_handled = False

        node = ast.parse(self.source)
        with self.sess:
            return self._run_node(node)

    def _run_node(self, node):
        typename = type(node).__name__
        fn = getattr(self, typename)
        try:
            return fn(node)
        except Exception:
            if not self.err_handled and hasattr(node, 'lineno'):
                line = self.source.split('\n')[node.lineno]
                src = f"{node.lineno} {line}"
                print(src, file=sys.stderr)
                print(" " * (len(f"{node.lineno} ") + node.col_offset) + "^", file=sys.stderr)
                self.err_handled = True
            raise

    def _run_nodes(self, nodes, env=None):
        block = B.EmptyBlock()
        with block:
            self.ctx.push(env)
            for node in nodes:
                res = self._run_node(node)
                if isinstance(res, B.Block):
                    block.add_statement(S.BlockStatement(res))
                elif isinstance(res, S.Statement):
                    block.add_statement(res)
                elif isinstance(res, list):
                    for s in res:
                        block.add_statement(s)
            self.ctx.pop()
        return block

    # ============= blocks =============
    def Module(self, node):
        return self._run_nodes(node.body)

    def ClassDef(self, node):
        raise NotImplementedError("class")

    def FunctionDef(self, node):
        name = node.name
        args = [self._run_node(arg) for arg in node.args.args]
        inputs = [(v.type, v.name) for v in args]
        returns = self._run_node(node.returns) if node.returns is not None else T.Void

        self.ctx[name] = V.Name(name)

        new_env = {v.name: v for v in args}
        block = self._run_nodes(node.body, new_env)
        return B.Function(name, inputs, returns, block.statements)

    def If(self, node):
        condition = self._run_node(node.test)
        block = self._run_nodes(node.body)
        block = B.If(condition, block.statements)

        orelse = node.orelse
        if not orelse:
            return block

        else_block = B.Else(self._run_nodes(orelse).statements)
        return [S.BlockStatement(block), S.BlockStatement(else_block)]

    def While(self, node):
        condition = self._run_node(node.test)
        block = self._run_nodes(node.body)
        return B.While(condition, block.statements)

    def For(self, node):
        target = self._run_node(node.target)
        if node.iter.func.id != "range":
            raise SyntaxError("Only support for-range")
        args = [self._run_node(x) for x in node.iter.args]
        if len(args) == 1:
            start, stop, step = 0, args[0], 1
        elif len(args) == 2:
            start, stop, step = args[0], args[1], 1
        else:
            start, stop, step = args
        return B.For(target, start, stop, step, self._run_nodes(node.body).statements)

    # ============= statements =============
    def Import(self, node):
        for target in node.names:
            name = target.name
            alias = target.asname
            if alias is None:
                # import name
                # include <name>
                name = name.split(".")
                name[-1] = ".".join(name[-1].split("__"))
                name = "<" + os.path.join(name) + ">"
                return M.StatementMacro("include", name)
            else:
                # import name as alias
                # namespace alias = name
                name = functools.reduce(E.ScopeAnalysis, map(V.Name, name.split(".")))
                var = V.Variable(alias, T.OtherType(V.Name("namespace")))
                self.ctx[alias] = var
                return S.VariableDeclaration(var, name)

    def ImportFrom(self, node):
        for target in node.names:
            if target == "*":
                # from module import *
                # TODO: using namespace module
                raise NotImplementedError("import from *")
            else:
                # from module import name
                # auto name = module::name
                mod = functools.reduce(E.ScopeAnalysis, map(V.Name, node.module.split(".")))
                name = target.asname if target.asname is not None else target.name
                self.ctx[name] = E.ScopeAnalysis(mod, V.Name(target.name))

    def Pass(self, node):
        return S.SingleLineComment("pass")

    def Return(self, node):
        value = self._run_node(node.value)
        return S.ReturnValue(value)

    def Assign(self, node):
        target = self._run_node(node.targets[0])
        value = self._run_node(node.value)
        return S.Assign(target, value)

    def AugAssign(self, node):
        op_map = {
            ast.Add: S.InplaceAdd,
            ast.Sub: S.InplaceSubtract,
            ast.Mult: S.InplaceMultiply,
            ast.Div: S.InplaceDivide,
        }
        target = self._run_node(node.target)
        op = type(node.op)
        value = self._run_node(node.value)
        return op_map[op](target, value)

    def AnnAssign(self, node):
        varname = node.target.id
        value = self._run_node(node.value) if node.value is not None else None
        type = self._run_node(node.annotation)
        target = V.variable(varname, type)
        self.ctx[varname] = target
        return S.VariableDeclaration(target, value)

    # ============= expressions =============
    def Name(self, node):
        ctx = self.ctx
        name = node.id
        try:
            return ctx[name]
        except KeyError:
            raise NameError(f"Can't find name `{name}`")

    def Num(self, node):
        return E.Const(node.n)

    def Str(self, node):
        return E.Const(node.s)

    def Compare(self, node):
        op_mapping = {
            ast.Eq: E.CompareEQ,
            ast.NotEq: E.CompareNE,
            ast.Gt: E.CompareGT,
            ast.GtE: E.CompareGE,
            ast.Lt: E.CompareLT,
            ast.LtE: E.CompareLE,
        }
        op = op_mapping[type(node.ops[0])]
        target = self._run_node(node.left)
        value = self._run_node(node.comparators[0])
        return op(target, value)

    def Expression(self, node):
        return self._run_node(node.value)

    def Subscript(self, node):
        obj = self._run_node(node.value)
        index = self._run_node(node.slice)
        return obj[index]

    def Index(self, node):
        return self._run_node(node.value)

    def Slice(self, node):
        return slice(node.lower, node.upper, node.step)

    def ExtSlice(self, node):
        return tuple(map(self._run_node, node.dims))

    def Attribute(self, node):
        obj = self._run_node(node.value)
        return getattr(obj, node.attr)

    def BinOp(self, node):
        op_map = {
            ast.Add: E.BinaryAdd,
            ast.Sub: E.BinarySubtract,
            ast.Mult: E.BinaryMultiply,
            ast.Div: E.BinaryDivide,
            ast.Mod: E.BinaryModulo,
            ast.LShift: E.BinaryLShift,
            ast.RShift: E.BinaryRShift,
            ast.And: E.LogicalAnd,
            ast.Or: E.LogicalOr,
            ast.BitXor: E.BinaryXor,
            ast.BitAnd: E.BinaryAnd,
            ast.BitOr: E.BinaryOr,
        }
        op = op_map[type(node.op)]
        left = self._run_node(node.left)
        right = self._run_node(node.right)
        return op(left, right)

    def Call(self, node):
        func = self._run_node(node.func)
        args = tuple(self._run_node(x) for x in node.args)
        return E.CallFunction(func, args)

    def Tuple(self, node):
        return tuple(map(self._run_node, node.elts))

    def List(self, node):
        return list(map(self._run_node, node.elts))

    def IfExp(self, node):
        return E.IIf(
            self._run_node(node.test),
            self._run_node(node.body),
            self._run_node(node.orelse),
        )

    # ============= others =============
    def arg(self, node):
        return V.variable(node.arg, self._run_node(node.annotation))

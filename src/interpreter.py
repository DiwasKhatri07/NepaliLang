"""
NepaliCode Interpreter
======================

Executes the Abstract Syntax Tree produced by the parser.

Features:
- Scoped environments (lexical scoping, closures)
- Functions: defaults, *args, **kwargs, annotations, recursion, lambdas
- Classes: inheritance, methods, properties via attributes, special methods
  (__init__, __str__, __eq__, __add__, __getitem__, __iter__, ...), super()
- Exceptions: koshish/samau/antya, uthau, catchable runtime error classes
- Iterators and generators (yield), for-loops over any iterable
- break/continue, with-statement (__enter__/__exit__)
- f-strings, comprehensions, tuples, sets, slicing
- Value methods on built-in types (list.map(...), text.upper(), map.keys(), ...)
- Module system: .np modules preferred, Python-hosted stdlib supported
"""

from __future__ import annotations

import os
import queue as _queue
import threading
from typing import Any, Dict, List, Optional

from src.lexer import tokenize
from src.parser import (
    parse, Param,
    NumberNode, StringNode, FStringNode, BooleanNode, NullNode,
    VariableNode, BinaryOpNode, UnaryOpNode, LogicalOpNode,
    FunctionCallNode, AttributeNode, IndexNode, SliceNode,
    ListNode, TupleNode, MapNode, SetNode, LambdaNode, ComprehensionNode,
    AssignmentNode, AugAssignmentNode, AnnotationNode, ConstNode,
    FunctionDefNode, ReturnNode, IfNode, WhileNode, ForNode,
    BreakNode, ContinueNode, PassNode, ClassDefNode,
    TryNode, RaiseNode, WithNode, ImportNode, PrintNode, YieldNode,
    TernaryNode,
)
from src.errors import (
    NpError, NpNameError, NpTypeError, NpValueError, NpZeroDivisionError,
    NpIndexError, NpKeyError, NpAttributeError, NpImportError,
    NpStopIteration, did_you_mean,
)

__all__ = [
    "Interpreter", "interpret", "NepaliRuntimeError", "NpThrow",
    "NpFunction", "NpClass", "NpInstance", "NpModule", "NpRange",
    "NpGenerator", "BuiltinFunction", "Environment", "np_str", "np_bool",
]


# Backward-compatible alias (the editor imports this name).
NepaliRuntimeError = NpError


# ---------------------------------------------------------------------- #
# Control-flow signals
# ---------------------------------------------------------------------- #
class ReturnSignal(Exception):
    def __init__(self, value: Any) -> None:
        self.value = value


class BreakSignal(Exception):
    pass


class ContinueSignal(Exception):
    pass


class NpThrow(Exception):
    """A NepaliCode exception in flight (catchable by koshish/samau)."""

    def __init__(self, value: Any, node: Any = None) -> None:
        self.value = value
        self.node = node
        self.file = getattr(node, "file", None) or "<unknown>"
        self.line = getattr(node, "line", 0) or 0
        self.column = getattr(node, "column", 0) or 0
        super().__init__(np_str(value))


# ---------------------------------------------------------------------- #
# Environments
# ---------------------------------------------------------------------- #
class Environment:
    """A lexical scope: variable bindings plus a link to the enclosing scope."""

    __slots__ = ("vars", "types", "consts", "parent")

    def __init__(self, parent: Optional["Environment"] = None) -> None:
        self.vars: Dict[str, Any] = {}
        self.types: Dict[str, Any] = {}
        self.consts: set = set()
        self.parent = parent

    def get(self, name: str) -> tuple:
        """Return (found, value)."""
        env: Optional[Environment] = self
        while env is not None:
            if name in env.vars:
                return True, env.vars[name]
            env = env.parent
        return False, None

    def has(self, name: str) -> bool:
        found, _ = self.get(name)
        return found

    def declare(self, name: str, value: Any) -> None:
        self.vars[name] = value

    def assign(self, name: str, value: Any) -> bool:
        """Assign to an existing binding anywhere in the chain; else declare locally."""
        env: Optional[Environment] = self
        while env is not None:
            if name in env.vars:
                if name in env.consts:
                    raise NpError(f"Cannot assign to constant '{name}'")
                env.vars[name] = value
                return True
            env = env.parent
        self.vars[name] = value
        return False


# ---------------------------------------------------------------------- #
# Callable values
# ---------------------------------------------------------------------- #
class BuiltinFunction:
    __slots__ = ("name", "fn", "self_value")

    def __init__(self, name: str, fn, self_value: Any = None) -> None:
        self.name = name
        self.fn = fn
        self.self_value = self_value

    def __call__(self, *args, **kwargs):  # pragma: no cover - convenience
        if self.self_value is not None:
            return self.fn(self.self_value, *args, **kwargs)
        return self.fn(*args, **kwargs)


class NpFunction:
    """A user-defined kaam/lambda, carrying its defining environment."""

    __slots__ = ("name", "params", "body", "env", "is_generator",
                 "line", "column", "interp", "owner_class")

    def __init__(self, name: str, params: List[Param], body: List[Any],
                 env: Environment, interp: "Interpreter",
                 is_generator: bool = False, line: int = 0, column: int = 0) -> None:
        self.name = name or "<lambda>"
        self.params = params
        self.body = body
        self.env = env
        self.interp = interp
        self.is_generator = is_generator
        self.line = line
        self.column = column
        self.owner_class = None   # set for class methods


class NpBoundMethod:
    __slots__ = ("func", "instance")

    def __init__(self, func: NpFunction, instance: Any) -> None:
        self.func = func
        self.instance = instance


class SuperProxy:
    """`super` inside methods: resolves attributes starting one class up
    the MRO from the class where the currently-running method is defined.
    The instance is discovered from 'self' at call time, because the proxy
    is created before parameter binding."""

    __slots__ = ("cls", "instance")

    def __init__(self, cls: "NpClass", instance: Any = None) -> None:
        self.cls = cls
        self.instance = instance


class NpClass:
    __slots__ = ("name", "bases", "methods", "fields", "interp", "line", "column")

    def __init__(self, name: str, bases: List["NpClass"], methods: Dict[str, NpFunction],
                 fields: Dict[str, Any], interp: "Interpreter",
                 line: int = 0, column: int = 0) -> None:
        self.name = name
        self.bases = bases
        self.methods = methods
        self.fields = fields
        self.interp = interp
        self.line = line
        self.column = column

    def mro(self) -> List["NpClass"]:
        order = [self]
        visited = {self.name}
        for base in self.bases:
            for c in base.mro():
                if c.name not in visited:
                    visited.add(c.name)
                    order.append(c)
        return order

    def find_method(self, name: str) -> Optional[NpFunction]:
        for cls in self.mro():
            if name in cls.methods:
                return cls.methods[name]
        return None

    def find_field(self, name: str):
        for cls in self.mro():
            if name in cls.fields:
                return True, cls.fields[name]
        return False, None

    def is_subclass_of(self, other: "NpClass") -> bool:
        return any(c is other or c.name == other.name for c in self.mro())


class NpInstance:
    __slots__ = ("cls", "fields")

    def __init__(self, cls: NpClass) -> None:
        self.cls = cls
        self.fields: Dict[str, Any] = {}

    def get_attr(self, name: str):
        if name in self.fields:
            return True, self.fields[name]
        method = self.cls.find_method(name)
        if method is not None:
            return True, NpBoundMethod(method, self)
        found, value = self.cls.find_field(name)
        if found:
            return True, value
        return False, None

    def set_attr(self, name: str, value: Any) -> None:
        self.fields[name] = value


class NpModule:
    __slots__ = ("name", "namespace", "file")

    def __init__(self, name: str, namespace: Dict[str, Any], file: str = "") -> None:
        self.name = name
        self.namespace = namespace
        self.file = file

    def get_attr(self, name: str):
        if name in self.namespace:
            return True, self.namespace[name]
        return False, None


class NpRange:
    """The `a..b` range expression and the range() builtin (exclusive end)."""

    __slots__ = ("start", "stop", "step", "_range")

    def __init__(self, start: int, stop: int, step: int = 1) -> None:
        for v in (start, stop, step):
            if not isinstance(v, int) or isinstance(v, bool):
                raise NpValueError("range bounds must be whole numbers")
        self.start = start
        self.stop = stop
        self.step = step or 1
        self._range = range(start, stop, self.step)

    def __iter__(self):
        return iter(self._range)

    def __len__(self) -> int:
        return len(self._range)

    def __repr__(self) -> str:  # pragma: no cover
        return f"range({self.start}, {self.stop})" if self.step == 1 else \
               f"range({self.start}, {self.stop}, {self.step})"


class NpGenerator:
    """Thread-backed generator supporting yield/resume (experimental)."""

    def __init__(self, func: NpFunction, env: Environment) -> None:
        self.func = func
        self.env = env
        self._out: "_queue.Queue" = _queue.Queue()
        self._inbox: "_queue.Queue" = _queue.Queue()
        self._thread: Optional[threading.Thread] = None
        self._done = False
        self._pending_request: Optional[tuple] = None

    # -- protocol ------------------------------------------------------ #
    def __iter__(self):
        return self

    def _ensure_started(self) -> None:
        if self._thread is None:
            self._thread = threading.Thread(
                target=self._run_body, name=f"np-generator:{self.func.name}", daemon=True)
            self._thread.start()

    def _send(self, request: tuple):
        self._ensure_started()
        if self._done:
            raise NpStopIteration()
        self._inbox.put(request)
        kind, payload = self._out.get()
        if kind == "yield":
            return payload
        if kind == "return":
            self._done = True
            raise NpStopIteration()
        # error
        self._done = True
        raise payload

    def _run_body(self) -> None:
        interp = self.func.interp
        try:
            # self.env is the call environment with parameters already bound.
            call_env = self.env
            # Wait for the first request before starting execution.
            request = self._inbox.get()
            interp._generator_inbox = self._inbox
            interp._generator_out = self._out
            interp._push_env(call_env)
            try:
                for statement in self.func.body:
                    result = interp.execute(statement)
                    if isinstance(result, ReturnSignal):
                        self._out.put(("return", result.value))
                        return
                self._out.put(("return", None))
            finally:
                interp._pop_env()
                interp._generator_inbox = None
                interp._generator_out = None
        except NpThrow as t:
            self._out.put(("error", t))
        except ReturnSignal as r:
            self._out.put(("return", r.value))
        except (BreakSignal, ContinueSignal):
            self._out.put(("return", None))
        except NpStopIteration:
            self._out.put(("return", None))
        except Exception as exc:  # pragma: no cover - defensive
            self._out.put(("error", NpThrow(str(exc))))

    def __next__(self):
        return self._send(("next", None))

    def send_throw(self, exc: Exception):
        return self._send(("throw", exc))

    def close(self):
        if self._thread is not None and not self._done:
            self._done = True
            try:
                self._inbox.put(("close", None))
            except Exception:
                pass


# ---------------------------------------------------------------------- #
# Stringification (the language's single source of truth for display)
# ---------------------------------------------------------------------- #
def np_str(value: Any) -> str:
    if value is None:
        return "khali"
    if value is True:
        return "sacho"
    if value is False:
        return "jhut"
    if isinstance(value, str):
        return value
    if isinstance(value, float):
        return repr(value)
    if isinstance(value, list):
        return "[" + ", ".join(_repr(v) for v in value) + "]"
    if isinstance(value, tuple):
        return "(" + ", ".join(_repr(v) for v in value) + ("," if len(value) == 1 else "") + ")"
    if isinstance(value, set):
        if not value:
            return "set()"
        return "{" + ", ".join(_repr(v) for v in value) + "}"
    if isinstance(value, dict):
        if not value:
            return "{}"
        return "{" + ", ".join(f"{_repr(k)}: {_repr(v)}" for k, v in value.items()) + "}"
    if isinstance(value, NpRange):
        return repr(value)
    if isinstance(value, NpInstance):
        return _instance_str(value)
    if isinstance(value, NpClass):
        return f"<kakshya {value.name}>"
    if isinstance(value, (NpFunction, BuiltinFunction, NpBoundMethod)):
        name = getattr(value, "name", "<kaam>")
        return f"<kaam {name}>"
    if isinstance(value, NpModule):
        return f"<module {value.name}>"
    if isinstance(value, NpGenerator):
        return f"<generator {value.func.name}>"
    if isinstance(value, SuperProxy):
        return "<super>"
    return str(value)


def _repr(value: Any) -> str:
    if isinstance(value, str):
        escaped = value.replace("\\", "\\\\").replace('"', '\\"')
        return f'"{escaped}"'
    return np_str(value)


def _instance_str(instance: NpInstance) -> str:
    str_fn = instance.cls.find_method("__str__")
    if str_fn is not None:
        result = instance.cls.interp.call_function(str_fn, [instance])
        return np_str(result)
    parts = ", ".join(f"{k}={_repr(v)}" for k, v in instance.fields.items())
    return f"<{instance.cls.name} {parts}>" if parts else f"<{instance.cls.name}>"


def np_bool(value: Any) -> bool:
    if value is None:
        return False
    if isinstance(value, bool):
        return value
    if isinstance(value, NpInstance):
        return True
    if isinstance(value, NpRange):
        return len(value) > 0
    return bool(value)


# ---------------------------------------------------------------------- #
# Type names exposed by the type() builtin
# ---------------------------------------------------------------------- #
def np_type_name(value: Any) -> str:
    if value is None:
        return "khali"
    if isinstance(value, bool):
        return "bool"
    if isinstance(value, int):
        return "number"
    if isinstance(value, float):
        return "number"
    if isinstance(value, str):
        return "text"
    if isinstance(value, list):
        return "list"
    if isinstance(value, tuple):
        return "tuple"
    if isinstance(value, dict):
        return "map"
    if isinstance(value, set):
        return "set"
    if isinstance(value, NpRange):
        return "range"
    if isinstance(value, NpInstance):
        return value.cls.name
    if isinstance(value, NpClass):
        return "kakshya"
    if isinstance(value, (NpFunction, BuiltinFunction, NpBoundMethod)):
        return "kaam"
    if isinstance(value, NpModule):
        return "module"
    return type(value).__name__


# Mapping from annotation names to runtime types (for optional checking).
_TYPE_ALIASES = {
    "number": (int, float), "ank": (int, float),
    "text": (str,), "string": (str,), "str": (str,),
    "bool": (bool,), "list": (list,), "map": (dict,),
    "tuple": (tuple,), "set": (set,), "khali": (type(None),),
    "kaam": (NpFunction, BuiltinFunction, NpBoundMethod),
}


def _annotation_matches(value: Any, annotation: Any) -> bool:
    if isinstance(annotation, VariableNode):
        expected = _TYPE_ALIASES.get(annotation.name)
        if expected is None:
            return True  # unknown/class annotations: no check
        if isinstance(value, bool) and bool not in expected and (int, float) == expected:
            return False
        return isinstance(value, expected)
    if isinstance(annotation, ListNode) and annotation.elements:
        # [text] -> list of that type
        if isinstance(value, list):
            return all(_annotation_matches(v, annotation.elements[0]) for v in value)
        return False
    return True


# ---------------------------------------------------------------------- #
# The Interpreter
# ---------------------------------------------------------------------- #
class Interpreter:
    def __init__(self) -> None:
        self.globals = Environment()
        self.modules: Dict[str, NpModule] = {}
        self.module_cache_shared: bool = False
        self.search_paths: List[str] = []
        self.current_file = "<source>"
        self.source_lines: List[str] = []
        self._current_class_stack: List[Optional[NpClass]] = []
        self._tls = threading.local()
        self._generator_inbox: Optional[_queue.Queue] = None
        self._generator_out: Optional[_queue.Queue] = None
        # Shared mutable load-depth counter so circular imports are detected
        # even across nested module interpreters.
        self._load_counter = [0]
        self._install_builtins()

    # ------------------------------------------------------------------ #
    # Public API
    # ------------------------------------------------------------------ #
    def interpret(self, statements: List[Any]) -> Any:
        result = None
        try:
            for statement in statements:
                result = self.execute(statement)
        except ReturnSignal as signal:
            # A top-level 'firta' ends the script gracefully.
            result = signal.value
        return result

    def run_source(self, source: str, file: str = "<source>") -> Any:
        self.current_file = file
        self.source_lines = source.splitlines()
        self.search_paths.insert(0, os.path.dirname(os.path.abspath(file))
                                 if file != "<source>" else os.getcwd())
        statements = parse(tokenize(source, file=file), file=file,
                           source_lines=self.source_lines)
        try:
            return self.interpret(statements)
        except NpThrow as t:
            raise self._renderable_error(t) from None

    def execute_in_env(self, node: Any, env: Environment) -> Any:
        """Execute a node in a forced environment (class bodies, generators,
        comprehensions). Nested function calls push their own frame on top.
        The stack is thread-local, so generators running in their own thread
        never interfere with the caller's frames."""
        self._push_env(env)
        try:
            return self.execute(node)
        finally:
            self._pop_env()

    def _push_env(self, env: Environment) -> None:
        stack = getattr(self._tls, "stack", None)
        if stack is None:
            stack = []
            self._tls.stack = stack
        stack.append(env)

    def _pop_env(self) -> None:
        stack = getattr(self._tls, "stack", None)
        if stack:
            stack.pop()

    # ------------------------------------------------------------------ #
    # Environment access
    # ------------------------------------------------------------------ #
    def env(self) -> Environment:
        stack = getattr(self._tls, "stack", None)
        return stack[-1] if stack else self.globals

    def get_variable(self, name: str, node: Any = None) -> Any:
        found, value = self.env().get(name)
        if found:
            return value
        raise self._unknown_name(name, node)

    def set_variable(self, name: str, value: Any) -> None:
        self.env().assign(name, value)

    def declare_variable(self, name: str, value: Any) -> None:
        self.env().declare(name, value)

    def _unknown_name(self, name: str, node: Any = None) -> NpNameError:
        candidates = set(self.globals.vars.keys())
        env = self.env()
        while env is not None:
            candidates.update(env.vars.keys())
            env = env.parent
        for mod in self.modules.values():
            candidates.update(mod.namespace.keys())
        sugg = did_you_mean(name, sorted(candidates))
        err = NpNameError(f"Name '{name}' is not defined.",
                          suggestions=sugg)
        if node is not None:
            err.with_location(self.current_file, getattr(node, "line", 0),
                              getattr(node, "column", 0), self.source_lines)
        return err

    # ------------------------------------------------------------------ #
    # Error helpers (catchable NP exceptions)
    # ------------------------------------------------------------------ #
    def throw(self, cls_name: str, message: str, node: Any = None, suggestions: Optional[List[str]] = None) -> "NpThrow":
        instance = self.make_exception(cls_name, message)
        return NpThrow(instance, node)

    def make_exception(self, cls_name: str, message: str) -> NpInstance:
        base = self.globals.vars.get("Error")
        cls = self.globals.vars.get(cls_name)
        if not isinstance(cls, NpClass):
            cls = base
        instance = NpInstance(cls)
        instance.set_attr("message", message)
        return instance

    def _renderable_error(self, thrown: NpThrow) -> NpError:
        value = thrown.value
        message = value.fields.get("message", np_str(value)) \
            if isinstance(value, NpInstance) else np_str(value)
        cls_name = value.cls.name if isinstance(value, NpInstance) else "Error"
        code_map = {
            "TypeError": NpTypeError, "ValueError": NpValueError,
            "ZeroDivisionError": NpZeroDivisionError, "IndexError": NpIndexError,
            "KeyError": NpKeyError, "ImportError": NpImportError,
        }
        cls = code_map.get(cls_name, NpError)
        err = cls(f"{cls_name}: {message}" if cls is NpError else message)
        err.with_location(thrown.file, thrown.line, thrown.column)
        return err

    def _py_error_to_np(self, exc: Exception, node: Any) -> NpThrow:
        if isinstance(exc, RecursionError):
            return self.throw("RuntimeError", "Maximum recursion depth exceeded.", node)
        if isinstance(exc, ZeroDivisionError):
            return self.throw("ZeroDivisionError", "Division by zero.", node)
        if isinstance(exc, NpThrow):
            return exc
        return self.throw("RuntimeError", f"{type(exc).__name__}: {exc}", node)

    # ------------------------------------------------------------------ #
    # Statement execution
    # ------------------------------------------------------------------ #
    def execute(self, node: Any) -> Any:
        env = self.env()
        try:
            return self._execute(node, env)
        except NpError as err:
            if isinstance(err, NpNameError):
                raise
            if getattr(node, "line", 0) and err.line == 0:
                err.with_location(self.current_file, node.line, node.column,
                                  self.source_lines)
            raise
        except NpThrow as thrown:
            if thrown.line == 0 and getattr(node, "line", 0):
                thrown.file = self.current_file
                thrown.line = node.line
                thrown.column = node.column
            raise
        except ReturnSignal:
            raise
        except (BreakSignal, ContinueSignal):
            raise
        except NpStopIteration:
            raise self.throw("RuntimeError", "Iterator is exhausted.")
        except (RecursionError,) as exc:
            raise self._py_error_to_np(exc, node)
        except ZeroDivisionError as exc:
            raise self._py_error_to_np(exc, node)

    def _execute(self, node: Any, env: Environment) -> Any:
        if isinstance(node, (NumberNode, StringNode, BooleanNode)):
            return node.value
        if isinstance(node, NullNode):
            return None
        if isinstance(node, VariableNode):
            return self.get_variable(node.name, node)
        if isinstance(node, BinaryOpNode):
            return self._binary_op(node, env)
        if isinstance(node, UnaryOpNode):
            return self._unary_op(node, env)
        if isinstance(node, LogicalOpNode):
            if node.operator == "and":
                left = self.eval(node.left, env)
                return self.eval(node.right, env) if np_bool(left) else left
            left = self.eval(node.left, env)
            return left if np_bool(left) else self.eval(node.right, env)
        if isinstance(node, TernaryNode):
            if np_bool(self.eval(node.condition, env)):
                return self.eval(node.then, env)
            return self.eval(node.otherwise, env)
        if isinstance(node, AssignmentNode):
            return self._assign(node, env)
        if isinstance(node, AugAssignmentNode):
            return self._aug_assign(node, env)
        if isinstance(node, AnnotationNode):
            return self._declare(node, env, const=False)
        if isinstance(node, ConstNode):
            return self._declare(node, env, const=True)
        if isinstance(node, FunctionCallNode):
            return self._call(node, env)
        if isinstance(node, FunctionDefNode):
            return self._define_function(node, env)
        if isinstance(node, ReturnNode):
            value = self.eval(node.value, env) if node.value is not None else None
            raise ReturnSignal(value)
        if isinstance(node, YieldNode):
            return self._yield(node, env)
        if isinstance(node, IfNode):
            return self._if(node, env)
        if isinstance(node, WhileNode):
            return self._while(node, env)
        if isinstance(node, ForNode):
            return self._for(node, env)
        if isinstance(node, BreakNode):
            raise BreakSignal()
        if isinstance(node, ContinueNode):
            raise ContinueSignal()
        if isinstance(node, PassNode):
            return None
        if isinstance(node, ClassDefNode):
            return self._define_class(node, env)
        if isinstance(node, TryNode):
            return self._try(node, env)
        if isinstance(node, RaiseNode):
            return self._raise(node, env)
        if isinstance(node, WithNode):
            return self._with(node, env)
        if isinstance(node, ImportNode):
            return self._import(node, env)
        if isinstance(node, PrintNode):
            args = [self.eval(a, env) for a in node.args]
            self._builtin_print(*args)
            return None
        if isinstance(node, ListNode):
            return [self.eval(e, env) for e in node.elements]
        if isinstance(node, TupleNode):
            return tuple(self.eval(e, env) for e in node.elements)
        if isinstance(node, SetNode):
            return {self.eval(e, env) for e in node.elements}
        if isinstance(node, MapNode):
            return {self._map_key(self.eval(k, env)): self.eval(v, env)
                    for k, v in node.pairs}
        if isinstance(node, IndexNode):
            return self._index(node, env)
        if isinstance(node, SliceNode):
            return self._slice(node, env)
        if isinstance(node, AttributeNode):
            return self._attribute(node, env)
        if isinstance(node, FStringNode):
            return self._fstring(node, env)
        if isinstance(node, LambdaNode):
            return NpFunction("<lambda>", node.params, [ReturnNode(node.body)],
                              env, self, line=node.line, column=node.column)
        if isinstance(node, ComprehensionNode):
            return self._comprehension(node, env)
        raise NpError(f"Unknown AST node: {type(node).__name__}")

    def eval(self, node: Any, env: Optional[Environment] = None) -> Any:
        if env is None:
            return self.execute(node)
        return self.execute_in_env(node, env)

    # ------------------------------------------------------------------ #
    # Operators
    # ------------------------------------------------------------------ #
    def _binary_op(self, node: BinaryOpNode, env: Environment) -> Any:
        op = node.operator
        left = self.eval(node.left, env)
        right = self.eval(node.right, env)

        if op == "..":
            return self._make_range(left, right, node)

        # Give objects a chance via special methods.
        dunder = _OP_DUNDERS.get(op)
        if dunder and isinstance(left, NpInstance):
            method = left.cls.find_method(dunder)
            if method is not None:
                return self.call_function(method, [left, right], node=node)

        try:
            return _apply_binop(op, left, right)
        except NpThrow:
            raise
        except ZeroDivisionError:
            raise self.throw("ZeroDivisionError", "Division by zero.", node)
        except TypeError as exc:
            raise self.throw("TypeError",
                             f"Cannot apply '{op}' to {np_type_name(left)} "
                             f"and {np_type_name(right)}: {exc}", node)
        except Exception as exc:
            raise self._py_error_to_np(exc, node)

    def _make_range(self, left: Any, right: Any, node: Any) -> NpRange:
        if not isinstance(left, int) or not isinstance(right, int) or \
                isinstance(left, bool) or isinstance(right, bool):
            raise self.throw("TypeError", "Range bounds must be whole numbers.", node)
        return NpRange(left, right)

    def _unary_op(self, node: UnaryOpNode, env: Environment) -> Any:
        operand = self.eval(node.operand, env)
        if node.operator == "not":
            return not np_bool(operand)
        if node.operator == "-":
            if isinstance(operand, (int, float)) and not isinstance(operand, bool):
                return -operand
            raise self.throw("TypeError",
                             f"Cannot negate {np_type_name(operand)}.", node)
        raise self.throw("TypeError", f"Unknown unary operator {node.operator!r}.", node)

    def _map_key(self, key: Any) -> Any:
        # Map keys behave like Python dicts: strings/numbers/bools allowed.
        if isinstance(key, (str, int, float, bool, tuple)):
            return key
        return np_str(key)

    # ------------------------------------------------------------------ #
    # Assignment
    # ------------------------------------------------------------------ #
    def _assign(self, node: AssignmentNode, env: Environment) -> Any:
        value = self.eval(node.value, env)
        self._bind_target(node.target, value, env, node)
        return value

    def _aug_assign(self, node: AugAssignmentNode, env: Environment) -> Any:
        target = node.target
        if isinstance(target, VariableNode):
            found, current = env.get(target.name)
            if not found:
                raise self._unknown_name(target.name, node)
            try:
                value = _apply_binop(node.operator, current,
                                     self.eval(node.value, env))
            except ZeroDivisionError:
                raise self.throw("ZeroDivisionError", "Division by zero.", node)
            except TypeError as exc:
                raise self.throw("TypeError", str(exc), node)
            env.assign(target.name, value)
            self._check_annotation(env, target.name, value)
            return value
        if isinstance(target, IndexNode):
            container = self.eval(target.target, env)
            index = self.eval(target.index, env)
            found, current = self._index_value(container, index, target)
            value = _apply_binop(node.operator, current,
                                 self.eval(node.value, env))
            self._set_index(container, index, value, target)
            return value
        if isinstance(target, AttributeNode):
            obj = self.eval(target.target, env)
            found, current = self._attr_value(obj, target.attr, target)
            value = _apply_binop(node.operator, current,
                                 self.eval(node.value, env))
            self._set_attr(obj, target.attr, value, target)
            return value
        raise self.throw("TypeError", "Invalid assignment target.", node)

    def _declare(self, node, env: Environment, const: bool) -> Any:
        value = self.eval(node.value, env) if node.value is not None else None
        if const:
            env.consts.add(node.name)
        env.declare(node.name, value)
        if node.type_expr is not None:
            env.types[node.name] = node.type_expr
            self._check_annotation(env, node.name, value)
        return value

    def _check_annotation(self, env: Environment, name: str, value: Any) -> None:
        e: Optional[Environment] = env
        while e is not None:
            if name in e.types:
                if value is not None and not _annotation_matches(value, e.types[name]):
                    raise self.throw(
                        "TypeError",
                        f"Cannot assign {np_type_name(value)} to '{name}: "
                        f"{_annotation_str(e.types[name])}'.", None)
                return
            e = e.parent

    def _bind_target(self, target: Any, value: Any, env: Environment, node: Any) -> None:
        if isinstance(target, VariableNode):
            if target.name in env.consts:
                raise self.throw("TypeError",
                                 f"Cannot assign to constant '{target.name}'.", node)
            env.assign(target.name, value)
            self._check_annotation(env, target.name, value)
            return
        if isinstance(target, IndexNode):
            container = self.eval(target.target, env)
            index = self.eval(target.index, env)
            self._set_index(container, index, value, target)
            return
        if isinstance(target, AttributeNode):
            obj = self.eval(target.target, env)
            self._set_attr(obj, target.attr, value, target)
            return
        if isinstance(target, TupleNode) or (isinstance(target, ListNode)):
            # Unpacking: a, b = [1, 2]
            names = [t.name if isinstance(t, VariableNode) else None for t in target.elements]
            if any(n is None for n in names):
                raise self.throw("TypeError", "Invalid unpacking target.", node)
            values = list(value) if not isinstance(value, (str,)) else list(value)
            if len(names) != len(values):
                raise self.throw("ValueError",
                                 f"Cannot unpack {len(values)} values into "
                                 f"{len(names)} targets.", node)
            for n, v in zip(names, values):
                env.assign(n, v)
            return
        raise self.throw("TypeError", "Invalid assignment target.", node)

    # ------------------------------------------------------------------ #
    # Indexing / slicing / attributes
    # ------------------------------------------------------------------ #
    def _index(self, node: IndexNode, env: Environment) -> Any:
        target = self.eval(node.target, env)
        index = self.eval(node.index, env)
        # __getitem__ support
        if isinstance(target, NpInstance):
            method = target.cls.find_method("__getitem__")
            if method is not None:
                return self.call_function(method, [target, index], node=node)
        try:
            found, value = self._index_value(target, index, node)
        except NpThrow:
            raise
        except (TypeError, KeyError, IndexError) as exc:
            raise self.throw("TypeError" if isinstance(exc, TypeError) else
                             "IndexError", str(exc), node)
        if not found:
            raise self.throw("IndexError", f"Index {np_str(index)} out of range.", node)
        return value

    def _index_value(self, target: Any, index: Any, node: Any) -> tuple:
        if isinstance(target, (list, tuple, str)):
            if not isinstance(index, int) or isinstance(index, bool):
                raise self.throw("TypeError",
                                 f"{np_type_name(target)} indices must be whole numbers, "
                                 f"got {np_type_name(index)}.", node)
            if -len(target) <= index < len(target):
                return True, target[index]
            return False, None
        if isinstance(target, dict):
            if index in target:
                return True, target[index]
            skey = np_str(index)
            if skey in target:
                return True, target[skey]
            raise self.throw("KeyError", f"Key {np_str(index)} not found.", node)
        if isinstance(target, NpRange):
            if isinstance(index, int) and not isinstance(index, bool) and \
                    -len(target) <= index < len(target):
                return True, target._range[index]
            return False, None
        raise self.throw("TypeError",
                         f"Cannot index into {np_type_name(target)}.", node)

    def _set_index(self, container: Any, index: Any, value: Any, node: Any) -> None:
        if isinstance(container, list):
            if not isinstance(index, int) or isinstance(index, bool):
                raise self.throw("TypeError", "List indices must be whole numbers.", node)
            if -len(container) <= index < len(container):
                container[index] = value
                return
            raise self.throw("IndexError", "List assignment index out of range.", node)
        if isinstance(container, dict):
            container[self._map_key(index)] = value
            return
        if isinstance(container, NpInstance):
            method = container.cls.find_method("__setitem__")
            if method is not None:
                self.call_function(method, [container, index, value], node=node)
                return
        raise self.throw("TypeError",
                         f"Cannot assign into {np_type_name(container)}.", node)

    def _slice(self, node: SliceNode, env: Environment) -> Any:
        target = self.eval(node.target, env)
        start = self.eval(node.start, env) if node.start is not None else None
        stop = self.eval(node.stop, env) if node.stop is not None else None
        step = self.eval(node.step, env) if node.step is not None else None
        if isinstance(target, NpRange):
            target = list(target)
        try:
            return target[slice(start, stop, step)]
        except TypeError as exc:
            raise self.throw("TypeError", str(exc), node)

    def _attribute(self, node: AttributeNode, env: Environment) -> Any:
        obj = self.eval(node.target, env)
        try:
            found, value = self._attr_value(obj, node.attr, node)
        except NpThrow:
            raise
        except Exception as exc:
            raise self._py_error_to_np(exc, node)
        if not found:
            name = np_type_name(obj)
            raise self.throw("AttributeError",
                             f"'{name}' has no attribute '{node.attr}'.", node)
        return value

    def _attr_value(self, obj: Any, attr: str, node: Any = None) -> tuple:
        if isinstance(obj, NpInstance):
            # __getattr__ hook
            method = obj.cls.find_method("__getattr__")
            if method is not None:
                found, direct = obj.get_attr(attr)
                if found:
                    return True, direct
                return True, self.call_function(method, [obj, attr], node=node)
            return obj.get_attr(attr)
        if isinstance(obj, NpModule):
            return obj.get_attr(attr)
        if isinstance(obj, NpClass):
            if attr in obj.methods:
                return True, obj.methods[attr]
            found, value = obj.find_field(attr)
            if found:
                return True, value
            return False, None
        if isinstance(obj, SuperProxy):
            instance = obj.instance
            if instance is _SUPER_SENTINEL:
                # Discover 'self' from the current call frame.
                found, instance = self.env().get("self")
                if not found:
                    return False, None
            for cls in obj.cls.mro()[1:]:
                if attr in cls.methods:
                    return True, NpBoundMethod(cls.methods[attr], _SuperSelf(instance))
                found, value = cls.find_field(attr)
                if found:
                    return True, value
            return False, None
        if isinstance(obj, NpGenerator):
            return False, None
        method = _value_method(obj, attr, self)
        if method is not None:
            return True, method
        if attr == "message" and isinstance(obj, Exception):
            return True, str(obj)
        return False, None

    def _set_attr(self, obj: Any, attr: str, value: Any, node: Any) -> None:
        if isinstance(obj, NpInstance):
            obj.set_attr(attr, value)
            return
        if isinstance(obj, NpModule):
            raise self.throw("TypeError", "Cannot assign attributes on a module.", node)
        raise self.throw("AttributeError",
                         f"Cannot set attribute '{attr}' on {np_type_name(obj)}.", node)

    # ------------------------------------------------------------------ #
    # Calls
    # ------------------------------------------------------------------ #
    def _call(self, node: FunctionCallNode, env: Environment) -> Any:
        function = self.eval(node.function, env)
        args = [self.eval(a, env) for a in node.args]
        kwargs = {name: self.eval(v, env) for name, v in node.kwargs}
        for star in node.star_args:
            expanded = self.eval(star, env)
            if not isinstance(expanded, (list, tuple)):
                raise self.throw("TypeError",
                                 "Can only expand lists/tuples with * in calls.", node)
            args.extend(expanded)
        for dstar in node.double_star_kwargs:
            expanded = self.eval(dstar, env)
            if not isinstance(expanded, dict):
                raise self.throw("TypeError",
                                 "Can only expand maps with ** in calls.", node)
            kwargs.update(expanded)
        return self.call_value(function, args, kwargs, node)

    def call_value(self, function: Any, args: List[Any], kwargs: Dict[str, Any],
                   node: Any = None) -> Any:
        try:
            return self._call_impl(function, args, kwargs, node)
        except NpThrow:
            raise
        except (ReturnSignal, BreakSignal, ContinueSignal):
            raise
        except RecursionError:
            raise self.throw("RuntimeError",
                             "Maximum recursion depth exceeded.", node)
        except NpStopIteration:
            raise self.throw("RuntimeError", "Iterator is exhausted.", node)

    def _call_impl(self, function: Any, args: List[Any],
                   kwargs: Dict[str, Any], node: Any) -> Any:
        if isinstance(function, NpFunction):
            return self.call_function(function, args, kwargs, node)
        if isinstance(function, NpBoundMethod):
            instance = function.instance
            if isinstance(instance, _SuperSelf):
                # Bound via super: bind the real instance, and swallow an
                # explicit `self` argument if the user passed one.
                real = instance.instance
                if args and args[0] is real:
                    args = list(args[1:])
                return self.call_function(function.func,
                                          [real] + list(args), kwargs, node)
            return self.call_function(function.func,
                                      [instance] + list(args), kwargs, node)
        if isinstance(function, NpClass):
            return self.instantiate(function, args, kwargs, node)
        if isinstance(function, BuiltinFunction):
            if function.self_value is not None:
                return function.fn(function.self_value, *args, **kwargs)
            return function.fn(*args, **kwargs)
        if isinstance(function, NpInstance):
            call_fn = function.cls.find_method("__call__")
            if call_fn is not None:
                return self.call_function(call_fn, [function] + list(args), kwargs, node)
        if callable(function):
            return function(*args, **kwargs)
        raise self.throw("TypeError", f"{np_str(function)} is not callable.", node)

    def call_function(self, func: NpFunction, args: List[Any],
                      kwargs: Optional[Dict[str, Any]] = None, node: Any = None) -> Any:
        call_env = Environment(func.env)
        self._bind_params(func, args, kwargs or {}, call_env, node)

        # Inside methods, `super` resolves to a proxy over the defining
        # class MRO (skipping the class where the method was defined).
        if getattr(func, "owner_class", None) is not None:
            call_env.declare("super", SuperProxy(func.owner_class, _SUPER_SENTINEL))

        # Generators suspend instead of running to completion; the body
        # executes lazily in its own thread with the bound call environment.
        if func.is_generator:
            return NpGenerator(func, call_env)

        # Push a fresh frame; the body runs with its own environment.
        self._push_env(call_env)
        try:
            try:
                for statement in func.body:
                    self.execute(statement)
            except ReturnSignal as signal:
                return signal.value
            return None
        finally:
            self._pop_env()

    def _bind_params(self, func: NpFunction, args: List[Any],
                     kwargs: Dict[str, Any], call_env: Environment, node: Any) -> None:
        positional = list(args)
        star_values: List[Any] = []
        dstar_values: Dict[str, Any] = {}
        named_params = [p for p in func.params if p.kind == "normal"]

        # Bind positional args
        for param in named_params:
            if positional:
                call_env.declare(param.name, positional.pop(0))
            elif param.name in kwargs:
                call_env.declare(param.name, kwargs.pop(param.name))
            elif param.default is not None:
                call_env.declare(param.name, self.eval(param.default, func.env))
            else:
                raise self.throw("TypeError",
                                 f"{func.name}() missing required argument "
                                 f"'{param.name}'.", node or func)

        if positional:
            star_param = next((p for p in func.params if p.kind == "star"), None)
            if star_param is not None:
                star_values = positional
                positional = []
            else:
                raise self.throw("TypeError",
                                 f"{func.name}() takes {len(named_params)} argument(s) "
                                 f"but {len(args)} were given.", node or func)

        for param in func.params:
            if param.kind == "star":
                call_env.declare(param.name, star_values)
            elif param.kind == "doublestar":
                call_env.declare(param.name, dstar_values)

        # Remaining kwargs go to **kwargs
        dstar_param = next((p for p in func.params if p.kind == "doublestar"), None)
        if dstar_param is not None:
            dstar_values.update(kwargs)
        elif kwargs:
            first = next(iter(kwargs))
            raise self.throw("TypeError",
                             f"{func.name}() got an unexpected keyword "
                             f"argument '{first}'.", node or func)

    # ------------------------------------------------------------------ #
    # yield
    # ------------------------------------------------------------------ #
    def _yield(self, node: YieldNode, env: Environment) -> Any:
        inbox = self._generator_inbox
        if inbox is None:
            raise self.throw("TypeError",
                             "'firta dinu' can only be used inside a generator.", node)
        value = self.eval(node.value, env) if node.value is not None else None
        self._generator_out.put(("yield", value))
        request = inbox.get()
        kind, payload = request
        if kind == "throw":
            raise payload
        if kind == "close":
            raise ReturnSignal(None)
        return None

    # ------------------------------------------------------------------ #
    # Control flow
    # ------------------------------------------------------------------ #
    def _if(self, node: IfNode, env: Environment) -> Any:
        if np_bool(self.eval(node.condition, env)):
            return self._run_block(node.body, env)
        for condition, body in node.elif_branches:
            if np_bool(self.eval(condition, env)):
                return self._run_block(body, env)
        if node.else_body is not None:
            return self._run_block(node.else_body, env)
        return None

    def _while(self, node: WhileNode, env: Environment) -> Any:
        result = None
        iterations = 0
        while np_bool(self.eval(node.condition, env)):
            iterations += 1
            if iterations > _MAX_LOOP_ITERATIONS:
                raise self.throw("RuntimeError",
                                 "Loop exceeded the maximum iteration limit; "
                                 "is your condition ever false?", node)
            try:
                result = self._run_block(node.body, env)
            except BreakSignal:
                break
            except ContinueSignal:
                continue
        return result

    def _for(self, node: ForNode, env: Environment) -> Any:
        iterable = self.eval(node.iterable, env)
        result = None
        for item in self._iterate(iterable, node):
            if len(node.targets) == 1:
                env.assign(node.targets[0], item)
            else:
                values = list(item) if isinstance(item, (list, tuple)) else \
                    [item] * len(node.targets)
                if len(values) != len(node.targets):
                    raise self.throw("ValueError",
                                     f"Cannot unpack {len(values)} values into "
                                     f"{len(node.targets)} targets.", node)
                for name, v in zip(node.targets, values):
                    env.assign(name, v)
            try:
                result = self._run_block(node.body, env)
            except BreakSignal:
                break
            except ContinueSignal:
                continue
        return result

    def _iterate(self, iterable: Any, node: Any):
        if isinstance(iterable, NpInstance):
            iter_fn = iterable.cls.find_method("__iter__")
            if iter_fn is not None:
                it = self.call_function(iter_fn, [iterable], node=node)
                return self._iterate(it, node)
            next_fn = iterable.cls.find_method("__next__")
            if next_fn is not None:
                return self._instance_iterator(iterable, next_fn)
            raise self.throw("TypeError",
                             f"{np_type_name(iterable)} is not iterable.", node)
        if isinstance(iterable, NpGenerator):
            return self._generator_iterator(iterable)
        if isinstance(iterable, bool):
            raise self.throw("TypeError", "bool is not iterable.", node)
        if isinstance(iterable, int):
            return range(iterable)
        if isinstance(iterable, float):
            raise self.throw("TypeError", "Cannot iterate over a number.", node)
        if isinstance(iterable, (list, tuple, str, set, dict)):
            return iterable
        if isinstance(iterable, NpRange):
            return iterable
        if callable(iterable):
            try:
                it = iter(iterable)
                return self._py_iterator(it)
            except TypeError:
                pass
        raise self.throw("TypeError",
                         f"Cannot iterate over {np_type_name(iterable)}.", node)

    def _py_iterator(self, iterator):
        """Drives a raw Python iterator protocol via __next__ so that queue/
        thread-backed values surface NpStopIteration correctly."""
        while True:
            try:
                yield iterator.__next__()
            except StopIteration:
                return

    def _instance_iterator(self, instance: NpInstance, next_fn):
        while True:
            try:
                yield self.call_function(next_fn, [instance])
            except NpStopIteration:
                return

    def _generator_iterator(self, gen: NpGenerator):
        while True:
            try:
                yield gen.__next__()
            except NpStopIteration:
                gen.close()
                return

    def _run_block(self, body: List[Any], env: Environment) -> Any:
        result = None
        for statement in body:
            result = self.execute(statement)
            if isinstance(result, ReturnSignal):
                return result
        return result

    # ------------------------------------------------------------------ #
    # try / raise / with
    # ------------------------------------------------------------------ #
    def _try(self, node: TryNode, env: Environment) -> Any:
        result = None
        try:
            try:
                result = self._run_block(node.body, env)
            except (ReturnSignal, BreakSignal, ContinueSignal):
                raise
            except NpThrow as thrown:
                for exc_name, bind_name, handler_body in node.handlers:
                    if self._handler_matches(thrown, exc_name):
                        if bind_name:
                            env.assign(bind_name, thrown.value)
                        result = self._run_block(handler_body, env)
                        break
                else:
                    raise
            else:
                # No exception: run the else-block
                if node.else_body is not None:
                    result = self._run_block(node.else_body, env)
        finally:
            if node.finally_body is not None:
                self._run_block(node.finally_body, env)
        return result

    def _handler_matches(self, thrown: NpThrow, exc_name: Optional[str]) -> bool:
        if exc_name is None:
            return True
        value = thrown.value
        if isinstance(value, NpInstance):
            return any(c.name == exc_name for c in value.cls.mro())
        return exc_name in ("Error", "RuntimeError", "Exception")

    def _raise(self, node: RaiseNode, env: Environment) -> Any:
        if node.value is None:
            raise self.throw("Error", "Exception raised.", node)
        value = self.eval(node.value, env)
        if isinstance(value, NpInstance):
            raise NpThrow(value, node)
        if isinstance(value, NpClass):
            instance = NpInstance(value)
            init = value.find_method("__init__")
            if init is not None:
                self.call_function(init, [instance])
            raise NpThrow(instance, node)
        raise NpThrow(self.make_exception("Error", np_str(value)), node)

    def _with(self, node: WithNode, env: Environment) -> Any:
        result = None
        entered = []
        try:
            for expr, bind in node.items:
                manager = self.eval(expr, env)
                enter = self._lookup_dunder(manager, "__enter__")
                if enter is None:
                    raise self.throw("TypeError",
                                     f"{np_type_name(manager)} cannot be used "
                                     f"in 'bhitra' (no __enter__).", node)
                value = self.call_value(enter, [], {}, node)
                if bind:
                    env.assign(bind, value)
                entered.append((manager, value))
            result = self._run_block(node.body, env)
        finally:
            for manager, _ in reversed(entered):
                exit_fn = self._lookup_dunder(manager, "__exit__")
                if exit_fn is not None:
                    self.call_value(exit_fn, [], {}, node)
        return result

    def _lookup_dunder(self, obj: Any, name: str):
        if isinstance(obj, NpInstance):
            method = obj.cls.find_method(name)
            if method is not None:
                return NpBoundMethod(method, obj)
            return None
        if isinstance(obj, BuiltinFunction):
            return None
        return None

    # ------------------------------------------------------------------ #
    # Functions and classes
    # ------------------------------------------------------------------ #
    def _define_function(self, node: FunctionDefNode, env: Environment) -> NpFunction:
        is_gen = _contains_yield(node.body)
        func = NpFunction(node.name, node.params, node.body, env, self,
                          is_generator=is_gen, line=node.line, column=node.column)
        env.assign(node.name, func)
        return func

    def _define_class(self, node: ClassDefNode, env: Environment) -> NpClass:
        bases = []
        for base_expr in node.bases:
            base = self.eval(base_expr, env)
            if not isinstance(base, NpClass):
                raise self.throw("TypeError",
                                 "Class bases must be classes.", node)
            bases.append(base)
        cls = NpClass(node.name, bases, {}, {}, self, node.line, node.column)
        env.assign(node.name, cls)

        class_env = Environment(env)
        self._current_class_stack.append(cls)
        try:
            for statement in node.body:
                if isinstance(statement, FunctionDefNode):
                    func = NpFunction(statement.name, statement.params,
                                      statement.body, class_env, self,
                                      is_generator=_contains_yield(statement.body),
                                      line=statement.line, column=statement.column)
                    func.owner_class = cls
                    cls.methods[statement.name] = func
                else:
                    self.execute_in_env(statement, class_env)
            # Class-level constants become class fields
            for name, value in class_env.vars.items():
                if not isinstance(value, (NpFunction,)):
                    cls.fields[name] = value
        finally:
            self._current_class_stack.pop()
        return cls

    def instantiate(self, cls: NpClass, args: List[Any],
                    kwargs: Dict[str, Any], node: Any = None) -> NpInstance:
        instance = NpInstance(cls)
        init = cls.find_method("__init__")
        if init is not None:
            self.call_function(init, [instance] + list(args), kwargs, node)
        elif args or kwargs:
            raise self.throw("TypeError",
                             f"{cls.name}() takes no arguments.", node)
        return instance

    def _instantiate_builtin_error(self, cls: NpClass, message: str) -> NpInstance:
        instance = NpInstance(cls)
        instance.set_attr("message", message)
        return instance

    # ------------------------------------------------------------------ #
    # Comprehensions
    # ------------------------------------------------------------------ #
    def _comprehension(self, node: ComprehensionNode, env: Environment) -> Any:
        iterable = self.eval(node.iterable, env)
        results: List[Any] = []
        for item in self._iterate(iterable, node):
            comp_env = Environment(env)
            comp_env.declare(node.target, item)
            if node.conditions and not all(
                np_bool(self.eval(cond, comp_env)) for cond in node.conditions
            ):
                continue
            if node.kind == "map":
                key = self.eval(node.key, comp_env)
                value = self.eval(node.value, comp_env)
                results.append((self._map_key(key), value))
            else:
                results.append(self.eval(node.element, comp_env))
        if node.kind == "map":
            return dict(results)
        if node.kind == "set":
            return {r for r in results}
        return results

    # ------------------------------------------------------------------ #
    # f-strings
    # ------------------------------------------------------------------ #
    def _fstring(self, node: FStringNode, env: Environment) -> str:
        out = []
        for part in node.parts:
            if isinstance(part, str):
                out.append(part)
            else:
                _, expr_source = part
                tokens = tokenize(expr_source, file=self.current_file)
                ast = parse(tokens, file=self.current_file,
                            source_lines=self.source_lines)
                if len(ast) != 1:
                    raise self.throw("TypeError",
                                     f"Invalid expression in f-string: {{{expr_source}}}",
                                     node)
                value = self.eval(ast[0], env)
                out.append(np_str(value))
        return "".join(out)

    # ------------------------------------------------------------------ #
    # Modules
    # ------------------------------------------------------------------ #
    def _import(self, node: ImportNode, env: Environment) -> Any:
        module = self._load_module(node.module, node)
        for local_name, original in node.aliases.items():
            if node.names:
                # from-import: bind the specific names
                if original == "*":
                    for name, value in module.namespace.items():
                        if not name.startswith("_"):
                            env.assign(name, value)
                    continue
                if original not in module.namespace:
                    raise self.throw("ImportError",
                                     f"Module '{node.module}' has no name "
                                     f"'{original}'.", node)
                env.assign(local_name, module.namespace[original])
            else:
                env.assign(local_name, module)
        return module

    def _load_module(self, name: str, node: Any) -> NpModule:
        if name in self.modules:
            return self.modules[name]
        if self._load_counter[0] > 40:
            raise self.throw("ImportError",
                             f"Circular or too-deep import detected for '{name}'.", node)
        file_path = self._find_module_file(name)
        if file_path is None:
            candidates = [m for m in self._available_module_names()]
            suggestions = did_you_mean(name, candidates)[:1]
            raise self.throw("ImportError",
                             f"Module '{name}' not found.", node,
                             suggestions=suggestions)
        self._load_counter[0] += 1
        try:
            if file_path.endswith(".np"):
                module = self._load_np_module(name, file_path)
            else:
                module = self._load_py_module(name, file_path)
            self.modules[name] = module
            return module
        finally:
            self._load_counter[0] -= 1

    def _find_module_file(self, name: str) -> Optional[str]:
        rel_np = name.replace(".", os.sep) + ".np"
        rel_py = name.replace(".", os.sep) + ".py"
        search = list(self.search_paths)
        search.append(os.getcwd())
        project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        search.append(os.path.join(project_root, "stdlib"))
        for directory in search:
            if not directory:
                continue
            np_path = os.path.join(directory, rel_np)
            py_path = os.path.join(directory, rel_py)
            if os.path.isfile(np_path):
                return np_path
            if os.path.isfile(py_path):
                return py_path
        return None

    def _available_module_names(self) -> List[str]:
        names = set()
        project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        for directory in list(self.search_paths) + [os.getcwd(),
                                                    os.path.join(project_root, "stdlib")]:
            if directory and os.path.isdir(directory):
                for entry in os.listdir(directory):
                    if entry.endswith(".np") or entry.endswith(".py"):
                        names.add(os.path.splitext(entry)[0])
        return sorted(names)

    def _load_np_module(self, name: str, path: str) -> NpModule:
        with open(path, "r", encoding="utf-8") as handle:
            source = handle.read()
        module_interp = Interpreter()
        module_interp.modules = self.modules  # share module cache
        module_interp._load_counter = self._load_counter  # share depth guard
        module_interp.current_file = path
        module_interp.source_lines = source.splitlines()
        module_interp.search_paths = [os.path.dirname(os.path.abspath(path))]
        statements = parse(tokenize(source, file=path), file=path,
                           source_lines=module_interp.source_lines)
        try:
            module_interp.interpret(statements)
        except NpThrow as thrown:
            raise self.throw("ImportError",
                             f"Error while importing '{name}': "
                             f"{np_str(thrown.value)}", path) from None
        namespace = dict(module_interp.globals.vars)
        namespace["__name__"] = name
        namespace["__file__"] = path
        return NpModule(name, namespace, path)

    def _load_py_module(self, name: str, path: str) -> NpModule:
        with open(path, "r", encoding="utf-8") as handle:
            source = handle.read()
        namespace: Dict[str, Any] = {"__name__": name, "__file__": path}
        try:
            exec(compile(source, path, "exec"), namespace)
        except Exception as exc:
            raise self.throw("ImportError",
                             f"Error while importing '{name}': {exc}") from None
        
        # Check if the module has a _module_dict (for our standard library)
        if "_module_dict" in namespace and namespace["_module_dict"] is not None:
            public = namespace["_module_dict"]
        else:
            # Otherwise, export non-underscore names
            public = {k: v for k, v in namespace.items() if not k.startswith("_")}
        
        return NpModule(name, public, path)

    # ------------------------------------------------------------------ #
    # Builtins
    # ------------------------------------------------------------------ #
    def _install_builtins(self) -> None:
        g = self.globals
        g.vars.update({
            "print": BuiltinFunction("print", self._builtin_print),
            "len": BuiltinFunction("len", _builtin_len),
            "type": BuiltinFunction("type", np_type_name),
            "str": BuiltinFunction("str", np_str),
            "int": BuiltinFunction("int", _builtin_int),
            "float": BuiltinFunction("float", _builtin_float),
            "bool": BuiltinFunction("bool", np_bool),
            "list": BuiltinFunction("list", _builtin_list),
            "tuple": BuiltinFunction("tuple", _builtin_tuple),
            "set": BuiltinFunction("set", _builtin_set),
            "map": BuiltinFunction("map", _builtin_dict),
            "dict": BuiltinFunction("dict", _builtin_dict),
            "range": BuiltinFunction("range", _builtin_range),
            "sum": BuiltinFunction("sum", _builtin_sum),
            "min": BuiltinFunction("min", _builtin_min),
            "max": BuiltinFunction("max", _builtin_max),
            "abs": BuiltinFunction("abs", abs),
            "round": BuiltinFunction("round", _builtin_round),
            "input": BuiltinFunction("input", _builtin_input),
            "enumerate": BuiltinFunction("enumerate", _builtin_enumerate),
            "zip": BuiltinFunction("zip", _builtin_zip),
            "sorted": BuiltinFunction("sorted", _builtin_sorted),
            "reversed": BuiltinFunction("reversed", _builtin_reversed),
            "any": BuiltinFunction("any", _builtin_any),
            "all": BuiltinFunction("all", _builtin_all),
            "ord": BuiltinFunction("ord", ord),
            "chr": BuiltinFunction("chr", chr),
            "isinstance": BuiltinFunction("isinstance", self._builtin_isinstance),
            "yo": BuiltinFunction("yo", lambda v: v),  # legacy convenience
        })
        # Built-in exception classes
        error_cls = NpClass("Error", [], {}, {}, self)
        error_cls.methods["__init__"] = _error_init()
        g.vars["Error"] = error_cls
        for name in ("ValueError", "TypeError", "IndexError", "KeyError",
                     "ZeroDivisionError", "RuntimeError", "ImportError",
                     "StopIteration", "FileNotFoundError"):
            sub = NpClass(name, [error_cls], {}, {}, self)
            sub.methods["__init__"] = _error_init()
            g.vars[name] = sub

    def _builtin_isinstance(self, obj: Any, cls: Any) -> bool:
        if isinstance(cls, NpClass):
            return isinstance(obj, NpInstance) and obj.cls.is_subclass_of(cls)
        if isinstance(cls, str):
            expected = _TYPE_ALIASES.get(cls)
            if expected:
                return isinstance(obj, expected)
            return np_type_name(obj) == cls
        if isinstance(cls, type):
            return isinstance(obj, cls)
        return False

    def _builtin_print(self, *args) -> None:
        print(*[np_str(a) for a in args])


class _Literal:
    """Wraps an already-evaluated value so it can flow through _binary_op."""
    __slots__ = ("value",)

    def __init__(self, value: Any) -> None:
        self.value = value


class _FakeClass:
    """Minimal stand-in so handler matching works by name."""
    __slots__ = ("name",)

    def __init__(self, name: str) -> None:
        self.name = name


_MAX_LOOP_ITERATIONS = 50_000_000


class _SuperSentinel:
    """Marker meaning 'resolve the instance from self at attribute access'."""


_SUPER_SENTINEL = _SuperSentinel()


class _SuperSelf:
    """Wrapper so super() methods don't re-bind 'self' when it is passed
    explicitly: calling super.speak(self) or super.speak() both work."""

    __slots__ = ("instance",)

    def __init__(self, instance: NpInstance) -> None:
        self.instance = instance


def _contains_yield(body: List[Any]) -> bool:
    for statement in body:
        if isinstance(statement, YieldNode):
            return True
        if isinstance(statement, IfNode):
            if (_contains_yield(statement.body)
                    or _contains_yield(statement.else_body or [])
                    or any(_contains_yield(b) for _, b in statement.elif_branches)):
                return True
        if isinstance(statement, WhileNode) and _contains_yield(statement.body):
            return True
        if isinstance(statement, ForNode) and _contains_yield(statement.body):
            return True
        if isinstance(statement, TryNode):
            if _contains_yield(statement.body) or _contains_yield(statement.finally_body or []):
                return True
            if any(_contains_yield(h) for _, _, h in statement.handlers):
                return True
        if isinstance(statement, WithNode) and _contains_yield(statement.body):
            return True
    return False


def _error_init():
    def __init__(self, message="An error occurred."):
        self.set_attr("message", np_str(message))
    return BuiltinFunction("__init__", __init__)


# ---------------------------------------------------------------------- #
# Binary operator implementation over built-in values
# ---------------------------------------------------------------------- #
_OP_DUNDERS = {
    "+": "__add__", "-": "__sub__", "*": "__mul__", "/": "__truediv__",
    "%": "__mod__", "**": "__pow__", "==": "__eq__", "!=": "__ne__",
    "<": "__lt__", "<=": "__le__", ">": "__gt__", ">=": "__ge__",
    "in": "__contains__",
}


def _apply_binop(op: str, left: Any, right: Any) -> Any:
    if op == "+":
        if isinstance(left, str) or isinstance(right, str):
            return np_str(left) + np_str(right)
        if isinstance(left, list) and isinstance(right, list):
            return left + right
        if isinstance(left, tuple) and isinstance(right, tuple):
            return left + right
        if isinstance(left, set) and isinstance(right, set):
            return left | right
        return left + right
    if op == "-":
        if isinstance(left, set) and isinstance(right, set):
            return left - right
        return left - right
    if op == "*":
        return left * right
    if op == "/":
        return left / right
    if op == "//":
        return left // right
    if op == "%":
        return left % right
    if op == "**":
        return left ** right
    if op == "==":
        return _np_eq(left, right)
    if op == "!=":
        return not _np_eq(left, right)
    if op == "<":
        return left < right
    if op == "<=":
        return left <= right
    if op == ">":
        return left > right
    if op == ">=":
        return left >= right
    if op == "in":
        if isinstance(right, dict):
            return left in right or np_str(left) in right
        if isinstance(right, NpRange):
            return left in right._range
        return left in right
    raise NpValueError(f"Unknown operator '{op}'")


def _np_eq(left: Any, right: Any) -> bool:
    if isinstance(left, NpInstance) and isinstance(right, NpInstance):
        if left is right:
            return True
        method = left.cls.find_method("__eq__")
        if method is not None:
            return bool(left.cls.interp.call_function(method, [left, right]))
        return False
    if type(left) is bool or type(right) is bool:
        return left is right if isinstance(left, bool) and isinstance(right, bool) \
            else False
    try:
        return bool(left == right)
    except Exception:
        return False


# ---------------------------------------------------------------------- #
# Builtin function implementations
# ---------------------------------------------------------------------- #
def _builtin_len(obj: Any) -> int:
    if isinstance(obj, NpInstance):
        method = obj.cls.find_method("__len__")
        if method is not None:
            return int(obj.cls.interp.call_function(method, [obj]))
        raise NpTypeError(f"{np_type_name(obj)} has no length.")
    if isinstance(obj, NpRange):
        return len(obj)
    try:
        return len(obj)
    except TypeError:
        raise NpTypeError(f"{np_type_name(obj)} has no length.")


def _builtin_int(value: Any = 0, base: Any = None) -> int:
    if isinstance(value, bool):
        return int(value)
    if isinstance(value, (int, float)):
        return int(value)
    if isinstance(value, str):
        return int(value.strip(), 0 if base is None else int(base))
    if isinstance(value, NpInstance):
        method = value.cls.find_method("__int__")
        if method is not None:
            return int(value.cls.interp.call_function(method, [value]))
    raise NpTypeError(f"Cannot convert {np_type_name(value)} to int.")


def _builtin_float(value: Any = 0.0) -> float:
    if isinstance(value, (int, float)) and not isinstance(value, bool):
        return float(value)
    if isinstance(value, str):
        return float(value.strip())
    raise NpTypeError(f"Cannot convert {np_type_name(value)} to float.")


def _builtin_list(value: Any = None) -> list:
    if value is None:
        return []
    if isinstance(value, NpRange):
        return list(value._range)
    if isinstance(value, list):
        return list(value)
    if isinstance(value, (tuple, str, set, dict)):
        return list(value)
    if isinstance(value, NpGenerator):
        items = []
        while True:
            try:
                items.append(value.__next__())
            except NpStopIteration:
                value.close()
                return items
    if isinstance(value, NpInstance):
        method = value.cls.find_method("__iter__")
        if method is not None:
            return list(value.cls.interp.call_function(method, [value]))
    try:
        return list(value)
    except TypeError:
        raise NpTypeError(f"Cannot convert {np_type_name(value)} to list.")


def _builtin_tuple(value: Any = None) -> tuple:
    return tuple(_builtin_list(value))


def _builtin_set(value: Any = None) -> set:
    return set(_builtin_list(value))


def _builtin_dict(value: Any = None) -> dict:
    if value is None:
        return {}
    if isinstance(value, dict):
        return dict(value)
    raise NpTypeError(f"Cannot convert {np_type_name(value)} to map.")


def _builtin_range(*args) -> NpRange:
    if len(args) == 1:
        return NpRange(0, int(args[0]))
    if len(args) == 2:
        return NpRange(int(args[0]), int(args[1]))
    if len(args) == 3:
        return NpRange(int(args[0]), int(args[1]), int(args[2]))
    raise NpTypeError("range() takes 1 to 3 arguments.")


def _builtin_sum(iterable: Any, start: Any = 0) -> Any:
    total = start
    for item in iterable:
        total = total + item
    return total


def _builtin_min(*args, **kwargs) -> Any:
    if len(args) == 1:
        return min(args[0], **kwargs)
    return min(*args, **kwargs)


def _builtin_max(*args, **kwargs) -> Any:
    if len(args) == 1:
        return max(args[0], **kwargs)
    return max(*args, **kwargs)


def _builtin_round(value: Any, digits: int = 0) -> Any:
    return round(value, int(digits))


def _builtin_input(prompt: str = "") -> str:
    try:
        return input(np_str(prompt))
    except EOFError:
        return ""


def _builtin_enumerate(iterable: Any, start: int = 0):
    return enumerate(iterable, int(start))


def _builtin_zip(*iterables):
    return zip(*iterables)


def _builtin_sorted(iterable: Any, key=None, reverse: bool = False) -> list:
    if key is not None and callable(key):
        return sorted(_builtin_list(iterable), key=key, reverse=reverse)
    return sorted(_builtin_list(iterable), reverse=reverse)


def _builtin_reversed(iterable: Any):
    if isinstance(iterable, str):
        return iterable[::-1]
    return list(reversed(_builtin_list(iterable)))


def _builtin_any(iterable: Any) -> bool:
    return any(np_bool(v) for v in iterable)


def _builtin_all(iterable: Any) -> bool:
    return all(np_bool(v) for v in iterable)


# ---------------------------------------------------------------------- #
# Value methods (methods on built-in types)
# ---------------------------------------------------------------------- #
def _value_method(value: Any, name: str, interp: Interpreter):
    """Return a bound method for built-in values, or None."""
    table = _VALUE_METHODS.get(type(value))
    if table is None:
        # bool is a subclass of int; map bool to int methods where sensible
        if isinstance(value, bool):
            table = _VALUE_METHODS.get(bool)
        if table is None:
            return None
    fn = table.get(name)
    if fn is None:
        return None
    return BuiltinFunction(name, fn, self_value=value)


def _list_map(lst: list, fn) -> list:
    return [fn(item) for item in lst]


def _list_filter(lst: list, fn) -> list:
    return [item for item in lst if np_bool(fn(item))]


def _list_each(lst: list, fn):
    for item in lst:
        fn(item)
    return None


def _list_join(lst: list, sep: str = " ") -> str:
    return np_str(sep).join(np_str(item) for item in lst)


def _str_contains(s: str, sub: str) -> bool:
    return sub in s


def _dict_has(d: dict, key: Any) -> bool:
    return key in d or np_str(key) in d


def _set_has(s: set, item: Any) -> bool:
    return item in s


_VALUE_METHODS = {
    list: {
        "append": lambda lst, v: lst.append(v),
        "extend": lambda lst, other: lst.extend(other),
        "insert": lambda lst, i, v: lst.insert(int(i), v),
        "pop": lambda lst, *a: lst.pop(*[int(a[0])] if a else []),
        "remove": lambda lst, v: lst.remove(v),
        "clear": lambda lst: lst.clear(),
        "index": lambda lst, v: lst.index(v),
        "count": lambda lst, v: lst.count(v),
        "sort": lambda lst, **kw: lst.sort(**kw),
        "reverse": lambda lst: lst.reverse(),
        "copy": lambda lst: list(lst),
        "map": _list_map,
        "filter": _list_filter,
        "each": _list_each,
        "forEach": _list_each,
        "join": _list_join,
        "contains": lambda lst, v: v in lst,
        "first": lambda lst: lst[0] if lst else None,
        "last": lambda lst: lst[-1] if lst else None,
    },
    str: {
        "upper": str.upper,
        "lower": str.lower,
        "title": str.title,
        "capitalize": str.capitalize,
        "strip": str.strip,
        "lstrip": str.lstrip,
        "rstrip": str.rstrip,
        "split": lambda s, *a: s.split(*a),
        "replace": lambda s, a, b: s.replace(a, b),
        "startswith": str.startswith,
        "endswith": str.endswith,
        "find": str.find,
        "count": str.count,
        "join": lambda s, parts: s.join(np_str(p) for p in parts),
        "contains": _str_contains,
        "index": lambda s, sub: s.index(sub),
        "zfill": str.zfill,
        "ljust": str.ljust,
        "rjust": str.rjust,
        "center": str.center,
        "isdigit": str.isdigit,
        "isalpha": str.isalpha,
        "isalnum": str.isalnum,
        "isspace": str.isspace,
    },
    dict: {
        "keys": lambda d: list(d.keys()),
        "values": lambda d: list(d.values()),
        "items": lambda d: [(k, v) for k, v in d.items()],
        "get": lambda d, k, *default: d.get(k, default[0] if default else None),
        "pop": lambda d, k, *default: d.pop(k, *default),
        "update": lambda d, other: d.update(other),
        "setdefault": lambda d, k, v=None: d.setdefault(k, v),
        "has": _dict_has,
        "contains": _dict_has,
        "clear": lambda d: d.clear(),
        "copy": lambda d: dict(d),
    },
    set: {
        "add": lambda s, v: s.add(v),
        "remove": lambda s, v: s.remove(v),
        "discard": lambda s, v: s.discard(v),
        "clear": lambda s: s.clear(),
        "union": lambda s, other: s | set(other),
        "intersection": lambda s, other: s & set(other),
        "difference": lambda s, other: s - set(other),
        "has": _set_has,
        "contains": _set_has,
    },
    tuple: {
        "index": lambda t, v: t.index(v),
        "count": lambda t, v: t.count(v),
        "contains": lambda t, v: v in t,
    },
    bool: {},
}


# ---------------------------------------------------------------------- #
# Convenience API (backward compatible)
# ---------------------------------------------------------------------- #
def interpret(statements: List[Any]) -> Any:
    """Run a parsed AST in a fresh interpreter (legacy entry point)."""
    return Interpreter().interpret(statements)

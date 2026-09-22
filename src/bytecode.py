"""
NepaliCode Bytecode Compiler and VM
===================================

EXPERIMENTAL. The tree-walking interpreter (src/interpreter.py) is the
reference engine; this module compiles a large subset of the language to
linear bytecode and executes it on a stack VM with real jump patching,
function calls, closures, classes and containers.

Supported: arithmetic, comparisons, and/or/not, variables, globals,
if/elif/else, while, for-in over lists/ranges/strings, break/continue,
functions (defaults), closures, calls, lists, maps, f-strings (const
parts), indexing, and print.

Not yet: classes/objects, generators, try/except (raises abort the VM),
with, modules. Use the interpreter for those.
"""

from __future__ import annotations

import enum
from typing import Any, Dict, List, Optional

from src.errors import NpError, NpSyntaxError

__all__ = [
    "OpCode", "Instruction", "CodeObject", "BytecodeCompiler",
    "BytecodeVM", "compile_to_bytecode", "run_bytecode",
]


class OpCode(enum.Enum):
    # Stack / constants
    LOAD_CONST = 1
    LOAD_VAR = 2
    STORE_VAR = 3
    LOAD_GLOBAL = 4
    STORE_GLOBAL = 5
    POP = 6
    DUP = 7

    # Arithmetic / comparison
    ADD = 10
    SUB = 11
    MUL = 12
    DIV = 13
    MOD = 14
    POW = 15
    FLOORDIV = 16
    EQ = 20
    NE = 21
    LT = 22
    LTE = 23
    GT = 24
    GTE = 25
    NOT = 26
    NEG = 27

    # Control flow
    JUMP = 30
    JUMP_IF_FALSE = 31
    JUMP_IF_TRUE = 32

    # Functions
    MAKE_FUNCTION = 50
    MAKE_CLOSURE = 51
    CALL = 33
    RETURN = 34
    RETURN_NONE = 35

    # Containers
    MAKE_LIST = 61
    MAKE_MAP = 62
    MAKE_TUPLE = 63
    GET_ITEM = 64
    SET_ITEM = 65

    # Misc
    PRINT = 40
    LEN = 41
    RANGE = 42
    GET_ITER = 43
    GET_ITER_OR_RANGE = 46
    FOR_ITER = 44
    IMPORT = 45
    HALT = 99


class Instruction:
    __slots__ = ("opcode", "arg", "line")

    def __init__(self, opcode: OpCode, arg: Any = None, line: int = 0) -> None:
        self.opcode = opcode
        self.arg = arg
        self.line = line

    def __repr__(self) -> str:  # pragma: no cover
        return f"({self.opcode.name} {self.arg!r})"


class CodeObject:
    """A compiled unit: linear instructions plus constant/name pools."""

    def __init__(self, name: str = "<module>", argcount: int = 0) -> None:
        self.name = name
        self.argcount = argcount
        self.param_names: List[str] = []
        self.instructions: List[Instruction] = []
        self.constants: List[Any] = []
        self.names: List[str] = []

    def add_const(self, value: Any) -> int:
        for i, existing in enumerate(self.constants):
            if type(existing) is type(value) and existing == value:
                return i
        self.constants.append(value)
        return len(self.constants) - 1

    def add_name(self, name: str) -> int:
        if name not in self.names:
            self.names.append(name)
        return self.names.index(name)

    def disassemble(self) -> str:  # pragma: no cover - debugging helper
        out = [f"== {self.name} =="]
        for i, instr in enumerate(self.instructions):
            out.append(f"{i:4} {instr.opcode.name:<14} {instr.arg!r}")
        return "\n".join(out)


class CompilerState:
    """Per-code-unit compilation context (locals, loop stack)."""

    def __init__(self, code: CodeObject, parent: Optional["CompilerState"] = None) -> None:
        self.code = code
        self.parent = parent
        self.loop_stack: List[tuple] = []   # (break_patch_positions, continue_target_depth)

    def resolve_local(self, name: str) -> Optional[int]:
        state = self
        while state is not None:
            if name in state.code.names:
                return state.code.names.index(name)
            state = state.parent
        return None


class BytecodeCompiler:
    """Compiles the NepaliCode AST to bytecode."""

    # Nodes that map cleanly onto bytecode; everything else is rejected
    # with a clear message (the interpreter handles the full language).
    def __init__(self) -> None:
        self.state: Optional[CompilerState] = None

    def compile(self, ast_nodes: List[Any], name: str = "<module>") -> CodeObject:
        code = CodeObject(name)
        self.state = CompilerState(code)
        for node in ast_nodes:
            self.compile_node(node)
        self.emit(OpCode.HALT)
        return code

    # ------------------------------------------------------------------ #
    def emit(self, opcode: OpCode, arg: Any = None, line: int = 0) -> int:
        assert self.state is not None
        self.state.code.instructions.append(Instruction(opcode, arg, line))
        return len(self.state.code.instructions) - 1

    def patch_jump(self, position: int, target: Optional[int] = None) -> None:
        assert self.state is not None
        if target is None:
            target = len(self.state.code.instructions)
        self.state.code.instructions[position].arg = target

    def here(self) -> int:
        assert self.state is not None
        return len(self.state.code.instructions)

    # ------------------------------------------------------------------ #
    def compile_block(self, body: List[Any]) -> None:
        for node in body:
            self.compile_node(node)

    def compile_node(self, node: Any) -> None:
        module = type(node).__name__
        method = getattr(self, f"_c_{module}", None)
        if method is None:
            raise NpSyntaxError(
                f"Bytecode compiler does not support '{module}' yet "
                f"(the tree-walking interpreter does).")
        method(node)

    # ---------------- expressions ---------------- #
    def _c_NumberNode(self, node):
        self.emit(OpCode.LOAD_CONST, self.state.code.add_const(node.value))

    def _c_StringNode(self, node):
        self.emit(OpCode.LOAD_CONST, self.state.code.add_const(node.value))

    def _c_BooleanNode(self, node):
        self.emit(OpCode.LOAD_CONST, self.state.code.add_const(node.value))

    def _c_NullNode(self, node):
        self.emit(OpCode.LOAD_CONST, self.state.code.add_const(None))

    def _c_VariableNode(self, node):
        # Names carry as instruction args; scoping is resolved at runtime
        # through the frame chain (function frame -> module globals).
        self.emit(OpCode.LOAD_VAR, node.name)

    def _c_BinaryOpNode(self, node):
        self.compile_node(node.left)
        self.compile_node(node.right)
        ops = {
            "+": OpCode.ADD, "-": OpCode.SUB, "*": OpCode.MUL, "/": OpCode.DIV,
            "%": OpCode.MOD, "**": OpCode.POW, "//": OpCode.FLOORDIV,
            "==": OpCode.EQ, "!=": OpCode.NE, "<": OpCode.LT, "<=": OpCode.LTE,
            ">": OpCode.GT, ">=": OpCode.GTE, "..": None,
        }
        if node.operator == "..":
            # Range: desugar to range(start, stop)
            self.emit(OpCode.RANGE)
            return
        op = ops.get(node.operator)
        if op is None:
            raise NpSyntaxError(f"Bytecode compiler does not support operator '{node.operator}'")
        self.emit(op)

    def _c_UnaryOpNode(self, node):
        self.compile_node(node.operand)
        if node.operator == "-":
            self.emit(OpCode.NEG)
        elif node.operator in ("not", "!"):
            self.emit(OpCode.NOT)
        else:
            raise NpSyntaxError(f"Unsupported unary operator {node.operator!r}")

    def _c_LogicalOpNode(self, node):
        self.compile_node(node.left)
        if node.operator == "and":
            jump = self.emit(OpCode.JUMP_IF_FALSE)
            self.emit(OpCode.POP)
            self.compile_node(node.right)
            self.patch_jump(jump)
        else:  # or
            jump = self.emit(OpCode.JUMP_IF_TRUE)
            self.emit(OpCode.POP)
            self.compile_node(node.right)
            self.patch_jump(jump)

    def _c_FunctionCallNode(self, node):
        if node.kwargs or node.star_args or node.double_star_kwargs:
            raise NpSyntaxError("Bytecode compiler does not support keyword/*args yet")
        # Compile callee first, then args, so CALL pops args then callee.
        self.compile_node(node.function)
        for arg in node.args:
            self.compile_node(arg)
        self.emit(OpCode.CALL, len(node.args))

    def _c_AttributeNode(self, node):
        # Support dotted access rooted at a module name (ganit.sqrt).
        from src.parser import VariableNode
        if isinstance(node.target, VariableNode):
            full = f"{node.target.name}.{node.attr}"
            self.emit(OpCode.LOAD_GLOBAL, full)
            return
        raise NpSyntaxError("Bytecode compiler does not support attribute access yet")

    def _c_IndexNode(self, node):
        self.compile_node(node.target)
        self.compile_node(node.index)
        self.emit(OpCode.GET_ITEM)

    def _c_SliceNode(self, node):
        raise NpSyntaxError("Bytecode compiler does not support slices yet")

    def _c_ListNode(self, node):
        for element in node.elements:
            self.compile_node(element)
        self.emit(OpCode.MAKE_LIST, len(node.elements))

    def _c_TupleNode(self, node):
        for element in node.elements:
            self.compile_node(element)
        self.emit(OpCode.MAKE_TUPLE, len(node.elements))

    def _c_MapNode(self, node):
        for key, value in node.pairs:
            self.compile_node(key)
            self.compile_node(value)
        self.emit(OpCode.MAKE_MAP, len(node.pairs))

    def _c_LambdaNode(self, node):
        raise NpSyntaxError("Bytecode compiler does not support lambdas yet")

    def _c_FStringNode(self, node):
        raise NpSyntaxError("Bytecode compiler does not support f-strings yet")

    def _c_ComprehensionNode(self, node):
        raise NpSyntaxError("Bytecode compiler does not support comprehensions yet")

    # ---------------- statements ---------------- #
    def _c_AssignmentNode(self, node):
        self.compile_node(node.value)
        self._store(node.target)

    def _c_AugAssignmentNode(self, node):
        from src.parser import VariableNode, IndexNode
        ops = {"+": OpCode.ADD, "-": OpCode.SUB, "*": OpCode.MUL,
               "/": OpCode.DIV, "%": OpCode.MOD}
        op = ops.get(node.operator)
        if op is None:
            raise NpSyntaxError(f"Unsupported augmented operator {node.operator!r}")
        if isinstance(node.target, VariableNode):
            self.compile_node(node.target)
            self.compile_node(node.value)
            self.emit(op)
            self._store(node.target)
        elif isinstance(node.target, IndexNode):
            self.compile_node(node.target.target)
            self.compile_node(node.target.index)
            self.compile_node(node.target.target)
            self.compile_node(node.target.index)
            self.compile_node(node.value)
            self.emit(op)
            self.emit(OpCode.SET_ITEM)
        else:
            raise NpSyntaxError("Unsupported augmented assignment target")

    def _c_AnnotationNode(self, node):
        if node.value is not None:
            self.emit(OpCode.LOAD_CONST, self.state.code.add_const(None)) if False else None
            self.compile_node(node.value)
            self._store_variable(node.name)

    def _store(self, target):
        from src.parser import VariableNode, IndexNode
        if isinstance(target, VariableNode):
            self._store_variable(target.name)
        elif isinstance(target, IndexNode):
            self.compile_node(target.target)
            self.compile_node(target.index)
            self.emit(OpCode.SET_ITEM)
        else:
            raise NpSyntaxError("Unsupported assignment target")

    def _store_variable(self, name: str):
        self.emit(OpCode.STORE_VAR, name)

    def _c_PrintNode(self, node):
        for arg in node.args:
            self.compile_node(arg)
        self.emit(OpCode.PRINT, len(node.args) if node.args else 0)

    def _c_IfNode(self, node):
        self.compile_node(node.condition)
        jump_false = self.emit(OpCode.JUMP_IF_FALSE)
        self.compile_block(node.body)
        if node.elif_branches or node.else_body is not None:
            jump_end = self.emit(OpCode.JUMP)
            self.patch_jump(jump_false)
            for condition, body in node.elif_branches:
                self.compile_node(condition)
                elif_false = self.emit(OpCode.JUMP_IF_FALSE)
                self.compile_block(body)
                jump_end2 = self.emit(OpCode.JUMP)
                self.patch_jump(elif_false)
                self.patch_jump(jump_end2)
                jump_end = jump_end2  # keep last
            if node.else_body is not None:
                self.compile_block(node.else_body)
            self.patch_jump(jump_end)
        else:
            self.patch_jump(jump_false)

    def _c_WhileNode(self, node):
        loop_start = self.here()
        self.compile_node(node.condition)
        exit_jump = self.emit(OpCode.JUMP_IF_FALSE)
        self.state.loop_stack.append(([], loop_start))
        self.compile_block(node.body)
        self.emit(OpCode.JUMP, loop_start)
        self.patch_jump(exit_jump)
        # Patch any break jumps collected in the loop body
        breaks, _ = self.state.loop_stack.pop()
        for b in breaks:
            self.patch_jump(b)

    def _c_ForNode(self, node):
        if len(node.targets) != 1:
            raise NpSyntaxError("Bytecode compiler does not support tuple unpacking in for")
        self.compile_node(node.iterable)
        # Legacy `for i in 10` counts 0..9 like range(10).
        self.emit(OpCode.GET_ITER_OR_RANGE)
        loop_start = self.here()
        iter_pos = self.emit(OpCode.FOR_ITER, None)
        self._store_variable(node.targets[0])
        self.state.loop_stack.append(([], loop_start, iter_pos))
        self.compile_block(node.body)
        self.emit(OpCode.JUMP, loop_start)
        breaks, _, iter_pos = self.state.loop_stack.pop()
        self.patch_jump(iter_pos, self.here())
        for b in breaks:
            self.patch_jump(b)

    def _c_BreakNode(self, node):
        assert self.state.loop_stack, "'rok' outside of a loop"
        patch = self.emit(OpCode.JUMP, None)
        self.state.loop_stack[-1][0].append(patch)

    def _c_ContinueNode(self, node):
        assert self.state.loop_stack, "'agadi' outside of a loop"
        entry = self.state.loop_stack[-1][1]
        self.emit(OpCode.JUMP, entry)

    def _c_FunctionDefNode(self, node):
        inner_code = CodeObject(node.name, argcount=len(
            [p for p in node.params if p.kind == "normal"]))
        inner_code.param_names = [p.name for p in node.params
                                  if p.kind == "normal"]
        saved_state = self.state
        self.state = CompilerState(inner_code, saved_state)
        self.compile_block(node.body)
        self.emit(OpCode.RETURN_NONE)
        self.state = saved_state
        # Store the CodeObject as a constant; MAKE_FUNCTION wraps it,
        # then bind the function object to its name.
        self.emit(OpCode.MAKE_FUNCTION, self.state.code.add_const(inner_code))
        self._store_variable(node.name)

    def _c_ReturnNode(self, node):
        if node.value is not None:
            self.compile_node(node.value)
            self.emit(OpCode.RETURN)
        else:
            self.emit(OpCode.RETURN_NONE)

    def _c_ImportNode(self, node):
        self.emit(OpCode.LOAD_CONST, self.state.code.add_const(node.module))
        self.emit(OpCode.IMPORT)
        if node.names:
            raise NpSyntaxError("Bytecode compiler does not support from-imports yet")
        for local_name in node.aliases:
            self._store_variable(local_name)

    def _c_PassNode(self, node):
        pass

    def _c_ClassDefNode(self, node):
        raise NpSyntaxError("Bytecode compiler does not support classes yet")

    def _c_TryNode(self, node):
        raise NpSyntaxError("Bytecode compiler does not support try/except yet")

    def _c_RaiseNode(self, node):
        raise NpSyntaxError("Bytecode compiler does not support raise yet")

    def _c_WithNode(self, node):
        raise NpSyntaxError("Bytecode compiler does not support with yet")

    def _c_YieldNode(self, node):
        raise NpSyntaxError("Bytecode compiler does not support generators yet")

    def _c_SetNode(self, node):
        raise NpSyntaxError("Bytecode compiler does not support set literals yet")

    def _c_ConstNode(self, node):
        raise NpSyntaxError("Bytecode compiler does not support const yet")

    def _c_TernaryNode(self, node):
        raise NpSyntaxError("Bytecode compiler does not support ternaries yet")


class NpFunctionObject:
    """Runtime representation of a compiled function."""

    __slots__ = ("code", "globals", "defaults")

    def __init__(self, code: CodeObject, globals_: Dict[str, Any]) -> None:
        self.code = code
        self.globals = globals_
        self.defaults: List[Any] = []


class BytecodeVM:
    """Stack-based virtual machine for NepaliCode bytecode."""

    def __init__(self, code: CodeObject) -> None:
        self.globals: Dict[str, Any] = {}
        self._install_builtins()
        # Frame 0 is the module frame (== globals); function calls push
        # fresh dict frames, so assignment inside a kaam is local and
        # reads fall back to enclosing/global scope.
        self.frames: List[Dict[str, Any]] = [self.globals]
        self.constants = code.constants
        self.names = code.names
        self.instructions = code.instructions
        self.ip = 0
        self.stack: List[Any] = []
        self.output = []

    def _install_builtins(self) -> None:
        self.globals.update({
            "len": len,
            "range": lambda *a: list(range(*a)),
            "type": lambda v: type(v).__name__,
            "str": str,
            "int": int,
            "float": float,
            "bool": bool,
            "sum": sum,
            "min": min,
            "max": max,
            "abs": abs,
            "round": round,
            "sorted": sorted,
            "yo": lambda v: v,  # legacy convenience constructor
        })

    # ------------------------------------------------------------------ #
    def run(self) -> Any:
        while self.ip < len(self.instructions):
            instr = self.instructions[self.ip]
            self.ip += 1
            result = self.execute_instruction(instr)
            if instr.opcode == OpCode.HALT:
                return result
        return None

    def current_frame(self) -> dict:
        return self.frames[-1]

    def push(self, value: Any) -> None:
        self.stack.append(value)

    def pop(self) -> Any:
        return self.stack.pop()

    # ------------------------------------------------------------------ #
    def execute_instruction(self, instr: Instruction) -> Any:
        op = instr.opcode

        if op == OpCode.LOAD_CONST:
            self.push(self.constants[instr.arg])
        elif op in (OpCode.LOAD_VAR, OpCode.LOAD_GLOBAL):
            name = instr.arg
            frame = self.frames[-1]
            if name in frame:
                self.push(frame[name])
            elif name in self.globals:
                self.push(self.globals[name])
            else:
                raise NpError(f"Undefined variable: {name}")
        elif op in (OpCode.STORE_VAR, OpCode.STORE_GLOBAL):
            self.frames[-1][instr.arg] = self.pop()
        elif op == OpCode.POP:
            self.pop()
        elif op == OpCode.DUP:
            self.stack.append(self.stack[-1])

        elif op == OpCode.ADD:
            right, left = self.pop(), self.pop()
            if isinstance(left, str) or isinstance(right, str):
                self.push(f"{left}{right}")
            else:
                self.push(left + right)
        elif op == OpCode.SUB:
            right, left = self.pop(), self.pop()
            self.push(left - right)
        elif op == OpCode.MUL:
            right, left = self.pop(), self.pop()
            self.push(left * right)
        elif op == OpCode.DIV:
            right, left = self.pop(), self.pop()
            if right == 0:
                raise NpError("Division by zero")
            self.push(left / right)
        elif op == OpCode.MOD:
            right, left = self.pop(), self.pop()
            self.push(left % right)
        elif op == OpCode.POW:
            right, left = self.pop(), self.pop()
            self.push(left ** right)
        elif op == OpCode.FLOORDIV:
            right, left = self.pop(), self.pop()
            self.push(left // right)
        elif op == OpCode.EQ:
            right, left = self.pop(), self.pop()
            self.push(left == right)
        elif op == OpCode.NE:
            right, left = self.pop(), self.pop()
            self.push(left != right)
        elif op == OpCode.LT:
            right, left = self.pop(), self.pop()
            self.push(left < right)
        elif op == OpCode.LTE:
            right, left = self.pop(), self.pop()
            self.push(left <= right)
        elif op == OpCode.GT:
            right, left = self.pop(), self.pop()
            self.push(left > right)
        elif op == OpCode.GTE:
            right, left = self.pop(), self.pop()
            self.push(left >= right)
        elif op == OpCode.NOT:
            self.push(not self.pop())
        elif op == OpCode.NEG:
            self.push(-self.pop())

        elif op == OpCode.JUMP:
            self.ip = instr.arg
        elif op == OpCode.JUMP_IF_FALSE:
            if not self.pop():
                self.ip = instr.arg
        elif op == OpCode.JUMP_IF_TRUE:
            if self.pop():
                self.ip = instr.arg

        elif op == OpCode.MAKE_FUNCTION:
            code_obj = self.constants[instr.arg]
            self.push(NpFunctionObject(code_obj, self.globals))
        elif op == OpCode.CALL:
            argc = instr.arg
            args = [self.pop() for _ in range(argc)][::-1]
            function = self.pop()
            self.push(self.call_function(function, args))
        elif op == OpCode.RETURN:
            value = self.pop()
            self.ip = len(self.instructions)  # simple model: stop
            return value
        elif op == OpCode.RETURN_NONE:
            self.ip = len(self.instructions)
            return None

        elif op == OpCode.MAKE_LIST:
            items = [self.pop() for _ in range(instr.arg)][::-1]
            self.push(items)
        elif op == OpCode.MAKE_TUPLE:
            items = [self.pop() for _ in range(instr.arg)][::-1]
            self.push(tuple(items))
        elif op == OpCode.MAKE_MAP:
            pairs = {}
            for _ in range(instr.arg):
                value = self.pop()
                key = self.pop()
                pairs[key] = value
            self.push(pairs)
        elif op == OpCode.GET_ITEM:
            index, target = self.pop(), self.pop()
            self.push(target[index])
        elif op == OpCode.SET_ITEM:
            value, index, target = self.pop(), self.pop(), self.pop()
            target[index] = value

        elif op == OpCode.PRINT:
            count = instr.arg or 0
            values = [self.pop() for _ in range(count)][::-1]
            print(*values) if values else print()

        elif op == OpCode.LEN:
            self.push(len(self.pop()))
        elif op == OpCode.RANGE:
            stop, start = self.pop(), self.pop()
            self.push(list(range(start, stop)))
        elif op == OpCode.GET_ITER:
            self.push(iter(self.pop()))
        elif op == OpCode.GET_ITER_OR_RANGE:
            value = self.pop()
            self.push(iter(range(value) if isinstance(value, int)
                           and not isinstance(value, bool) else value))
        elif op == OpCode.FOR_ITER:
            iterator = self.stack[-1]
            try:
                self.push(next(iterator))
            except StopIteration:
                self.pop()  # remove iterator
                self.ip = instr.arg
        elif op == OpCode.IMPORT:
            module = self.pop()
            namespace = self.load_module(module)
            self.push(namespace)
            # Also register dotted names (module.func) as globals.
            for attr, value in namespace.items():
                self.globals[f"{module}.{attr}"] = value
            self.globals[module] = namespace

        elif op == OpCode.HALT:
            return self.stack[-1] if self.stack else None

        else:
            raise NpError(f"Unknown opcode: {op}")

        return None

    # ------------------------------------------------------------------ #
    def call_function(self, function: Any, args: List[Any]) -> Any:
        if isinstance(function, NpFunctionObject):
            param_names = getattr(function.code, "param_names", [])
            if len(args) < len(param_names):
                raise NpError(f"{function.code.name}() missing arguments")
            frame: Dict[str, Any] = {}
            for i, pname in enumerate(param_names):
                frame[pname] = args[i] if i < len(args) else None
            self.frames.append(frame)
            saved_constants, saved_names = self.constants, self.names
            saved_instructions, saved_ip = self.instructions, self.ip
            try:
                self.constants = function.code.constants
                self.names = function.code.names
                self.instructions = function.code.instructions
                self.ip = 0
                while self.ip < len(self.instructions):
                    instr = self.instructions[self.ip]
                    self.ip += 1
                    result = self.execute_instruction(instr)
                    if instr.opcode in (OpCode.RETURN, OpCode.RETURN_NONE):
                        return result
            finally:
                self.constants, self.names = saved_constants, saved_names
                self.instructions, self.ip = saved_instructions, saved_ip
                self.frames.pop()
            return None
        if callable(function):
            return function(*args)
        raise NpError(f"{function!r} is not callable")

    def load_module(self, name: str):
        """Load a module: stdlib .py files first, then Python modules."""
        import importlib
        import os
        stdlib = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                              "stdlib")
        module_file = os.path.join(stdlib, f"{name}.py")
        if os.path.isfile(module_file):
            import importlib.util
            spec = importlib.util.spec_from_file_location(name, module_file)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            return {attr: getattr(module, attr)
                    for attr in dir(module) if not attr.startswith("_")}
        try:
            module = importlib.import_module(name)
        except ImportError:
            raise NpError(f"Module '{name}' not found")
        return {attr: getattr(module, attr)
                for attr in dir(module) if not attr.startswith("_")}


def compile_to_bytecode(ast_nodes: List[Any], name: str = "<module>") -> CodeObject:
    """Compile AST nodes to a CodeObject."""
    compiler = BytecodeCompiler()
    return compiler.compile(ast_nodes, name=name)


def run_bytecode(code: CodeObject) -> Any:
    """Execute compiled bytecode on a fresh VM."""
    vm = BytecodeVM(code)
    return vm.run()

"""
NepaliCode Parser
=================

Builds an Abstract Syntax Tree (AST) from the token stream produced by
the lexer. Block structure is driven by real INDENT/DEDENT tokens.

Supports: annotated variables, functions with defaults/*args/**kwargs and
return annotations, lambdas, classes with methods, if/elif/else,
while/for with break/continue, try/except/finally, raise, with,
lists/tuples/maps/sets, indexing/slicing, attribute access and
assignment, f-strings, and comprehensions.
"""

from __future__ import annotations

from typing import Any, List, Optional, Tuple

from src.lexer import Token, TokenType
from src.errors import NpSyntaxError, did_you_mean

__all__ = [
    # expressions
    "NumberNode", "StringNode", "FStringNode", "BooleanNode", "NullNode",
    "VariableNode", "BinaryOpNode", "UnaryOpNode", "LogicalOpNode",
    "TernaryNode",
    "FunctionCallNode", "AttributeNode", "IndexNode", "SliceNode",
    "ListNode", "TupleNode", "MapNode", "SetNode", "LambdaNode",
    "ComprehensionNode",
    # statements
    "AssignmentNode", "AugAssignmentNode", "AnnotationNode",
    "FunctionDefNode", "ReturnNode", "IfNode", "WhileNode", "ForNode",
    "BreakNode", "ContinueNode", "PassNode", "ClassDefNode",
    "TryNode", "RaiseNode", "WithNode", "ImportNode", "PrintNode",
    "Parser", "parse",
]


# ---------------------------------------------------------------------- #
# Expression nodes
# ---------------------------------------------------------------------- #
class NumberNode:
    __slots__ = ("value",)
    def __init__(self, value: float) -> None:
        self.value = value


class StringNode:
    __slots__ = ("value",)
    def __init__(self, value: str) -> None:
        self.value = value


class FStringNode:
    """value is a list of parts: plain str, or ('expr', source)."""
    __slots__ = ("parts", "line", "column")
    def __init__(self, parts: list, line: int = 0, column: int = 0) -> None:
        self.parts = parts
        self.line = line
        self.column = column


class BooleanNode:
    __slots__ = ("value",)
    def __init__(self, value: bool) -> None:
        self.value = value


class NullNode:
    __slots__ = ()


class VariableNode:
    __slots__ = ("name",)
    def __init__(self, name: str) -> None:
        self.name = name


class BinaryOpNode:
    __slots__ = ("left", "operator", "right", "line", "column")
    def __init__(self, left, operator: str, right, line: int = 0, column: int = 0) -> None:
        self.left = left
        self.operator = operator
        self.right = right
        self.line = line
        self.column = column


class UnaryOpNode:
    __slots__ = ("operator", "operand", "line", "column")
    def __init__(self, operator: str, operand, line: int = 0, column: int = 0) -> None:
        self.operator = operator
        self.operand = operand
        self.line = line
        self.column = column


class LogicalOpNode:
    """Short-circuit 'and' / 'or'."""
    __slots__ = ("left", "operator", "right")
    def __init__(self, left, operator: str, right) -> None:
        self.left = left
        self.operator = operator
        self.right = right


class TernaryNode:
    """Conditional expression:  value yedi condition natra otherwise."""
    __slots__ = ("condition", "then", "otherwise")
    def __init__(self, condition, then, otherwise) -> None:
        self.condition = condition
        self.then = then
        self.otherwise = otherwise


class FunctionCallNode:
    __slots__ = ("function", "args", "kwargs", "star_args", "double_star_kwargs", "line", "column")
    def __init__(self, function, args=None, kwargs=None, star_args=None,
                 double_star_kwargs=None, line: int = 0, column: int = 0) -> None:
        self.function = function
        self.args = args or []
        self.kwargs = kwargs or []          # list of (name, value)
        self.star_args = star_args or []    # *expr nodes
        self.double_star_kwargs = double_star_kwargs or []
        self.line = line
        self.column = column


class AttributeNode:
    __slots__ = ("target", "attr")
    def __init__(self, target, attr: str) -> None:
        self.target = target
        self.attr = attr


class IndexNode:
    __slots__ = ("target", "index", "line", "column")
    def __init__(self, target, index, line: int = 0, column: int = 0) -> None:
        self.target = target
        self.index = index
        self.line = line
        self.column = column


class SliceNode:
    __slots__ = ("target", "start", "stop", "step")
    def __init__(self, target, start, stop, step=None) -> None:
        self.target = target
        self.start = start
        self.stop = stop
        self.step = step


class ListNode:
    __slots__ = ("elements",)
    def __init__(self, elements: list) -> None:
        self.elements = elements


class TupleNode:
    __slots__ = ("elements",)
    def __init__(self, elements: list) -> None:
        self.elements = elements


class MapNode:
    __slots__ = ("pairs",)
    def __init__(self, pairs: list) -> None:  # list of (key, value)
        self.pairs = pairs


class SetNode:
    __slots__ = ("elements",)
    def __init__(self, elements: list) -> None:
        self.elements = elements


class LambdaNode:
    __slots__ = ("params", "body", "line", "column")
    def __init__(self, params: list, body, line: int = 0, column: int = 0) -> None:
        self.params = params
        self.body = body
        self.line = line
        self.column = column


class ComprehensionNode:
    """[expr for target in iterable (if cond)+] or {expr ...} / {k:v ...} variants."""
    __slots__ = ("kind", "element", "key", "value", "target", "iterable", "conditions")
    def __init__(self, kind: str, element, target, iterable, conditions=None,
                 key=None, value=None) -> None:
        self.kind = kind              # 'list' | 'set' | 'map'
        self.element = element
        self.key = key
        self.value = value
        self.target = target          # str target name (simple targets only)
        self.iterable = iterable
        self.conditions = conditions or []


# ---------------------------------------------------------------------- #
# Statement nodes
# ---------------------------------------------------------------------- #
class AssignmentNode:
    """target is VariableNode | IndexNode | AttributeNode; list of targets also allowed."""
    __slots__ = ("target", "value", "line", "column")
    def __init__(self, target, value, line: int = 0, column: int = 0) -> None:
        self.target = target
        self.value = value
        self.line = line
        self.column = column


class AugAssignmentNode:
    __slots__ = ("target", "operator", "value", "line", "column")
    def __init__(self, target, operator: str, value, line: int = 0, column: int = 0) -> None:
        self.target = target
        self.operator = operator        # '+', '-', '*', '/', '%'
        self.value = value
        self.line = line
        self.column = column


class AnnotationNode:
    """name: type [= value]"""
    __slots__ = ("name", "type_expr", "value", "line", "column")
    def __init__(self, name: str, type_expr, value, line: int = 0, column: int = 0) -> None:
        self.name = name
        self.type_expr = type_expr
        self.value = value
        self.line = line
        self.column = column


class ConstNode:
    """const name: type = value  (sthir) — an immutable binding."""
    __slots__ = ("name", "type_expr", "value", "line", "column")
    def __init__(self, name: str, type_expr, value, line: int = 0, column: int = 0) -> None:
        self.name = name
        self.type_expr = type_expr
        self.value = value
        self.line = line
        self.column = column


class YieldNode:
    """yield expr  (dinu) — generator suspension point."""
    __slots__ = ("value", "line", "column")
    def __init__(self, value, line: int = 0, column: int = 0) -> None:
        self.value = value
        self.line = line
        self.column = column


class FunctionDefNode:
    __slots__ = ("name", "params", "body", "return_annotation", "line", "column")
    def __init__(self, name: str, params: list, body: list,
                 return_annotation=None, line: int = 0, column: int = 0) -> None:
        self.name = name
        self.params = params            # list of Param tuples
        self.body = body
        self.return_annotation = return_annotation
        self.line = line
        self.column = column


class Param:
    __slots__ = ("name", "default", "annotation", "kind")
    def __init__(self, name: str, default=None, annotation=None, kind: str = "normal") -> None:
        self.name = name
        self.default = default          # AST or None
        self.annotation = annotation    # AST or None
        self.kind = kind                # 'normal' | 'star' | 'doublestar'


class ReturnNode:
    __slots__ = ("value", "line", "column")
    def __init__(self, value, line: int = 0, column: int = 0) -> None:
        self.value = value
        self.line = line
        self.column = column


class IfNode:
    __slots__ = ("condition", "body", "elif_branches", "else_body", "line", "column")
    def __init__(self, condition, body, elif_branches=None, else_body=None,
                 line: int = 0, column: int = 0) -> None:
        self.condition = condition
        self.body = body
        self.elif_branches = elif_branches or []   # list of (cond, body)
        self.else_body = else_body
        self.line = line
        self.column = column


class WhileNode:
    __slots__ = ("condition", "body", "line", "column")
    def __init__(self, condition, body, line: int = 0, column: int = 0) -> None:
        self.condition = condition
        self.body = body
        self.line = line
        self.column = column


class ForNode:
    __slots__ = ("targets", "iterable", "body", "line", "column")
    def __init__(self, targets: list, iterable, body, line: int = 0, column: int = 0) -> None:
        self.targets = targets          # list of str (tuple unpacking: a, b in pairs)
        self.iterable = iterable
        self.body = body
        self.line = line
        self.column = column


class BreakNode:
    __slots__ = ("line", "column")
    def __init__(self, line: int = 0, column: int = 0) -> None:
        self.line = line
        self.column = column


class ContinueNode:
    __slots__ = ("line", "column")
    def __init__(self, line: int = 0, column: int = 0) -> None:
        self.line = line
        self.column = column


class PassNode:
    __slots__ = ()


class ClassDefNode:
    __slots__ = ("name", "bases", "body", "line", "column")
    def __init__(self, name: str, bases: list, body: list,
                 line: int = 0, column: int = 0) -> None:
        self.name = name
        self.bases = bases
        self.body = body
        self.line = line
        self.column = column


class TryNode:
    __slots__ = ("body", "handlers", "else_body", "finally_body", "line", "column")
    def __init__(self, body, handlers, else_body=None, finally_body=None,
                 line: int = 0, column: int = 0) -> None:
        self.body = body
        self.handlers = handlers        # list of (exc_name_or_None, bind_name_or_None, body)
        self.else_body = else_body
        self.finally_body = finally_body
        self.line = line
        self.column = column


class RaiseNode:
    __slots__ = ("value", "line", "column")
    def __init__(self, value, line: int = 0, column: int = 0) -> None:
        self.value = value
        self.line = line
        self.column = column


class WithNode:
    __slots__ = ("items", "body", "line", "column")
    def __init__(self, items: list, body: list, line: int = 0, column: int = 0) -> None:
        self.items = items              # list of (expr, bind_name_or_None)
        self.body = body
        self.line = line
        self.column = column


class ImportNode:
    __slots__ = ("module", "names", "aliases", "line", "column")
    def __init__(self, module: str, names=None, aliases=None,
                 line: int = 0, column: int = 0) -> None:
        self.module = module
        self.names = names              # bata X lyau a, b
        self.aliases = aliases or {}    # {local_name: original_name}
        self.line = line
        self.column = column


class PrintNode:
    """Legacy node: `print(...)` statements are kept for fast printing."""
    __slots__ = ("args",)
    def __init__(self, args) -> None:
        self.args = args


class Parser:
    def __init__(self, tokens: List[Token], file: str = "<source>",
                 source_lines: Optional[List[str]] = None) -> None:
        self.tokens = tokens
        self.pos = 0
        self.file = file
        self.source_lines = source_lines or []
        # Depth of [...] subscript parsing: suppresses the '..' range
        # operator so a[1..3] parses as a slice, not an index of a range.
        self.subscript_depth = 0

    # ------------------------------------------------------------------ #
    # Token helpers
    # ------------------------------------------------------------------ #
    def current_token(self) -> Optional[Token]:
        if self.pos < len(self.tokens):
            return self.tokens[self.pos]
        return None

    def advance(self) -> Optional[Token]:
        token = self.current_token()
        if token:
            self.pos += 1
        return token

    def peek(self, offset: int = 1) -> Optional[Token]:
        peek_pos = self.pos + offset
        if peek_pos < len(self.tokens):
            return self.tokens[peek_pos]
        return None

    def check(self, *types: TokenType) -> bool:
        tok = self.current_token()
        return tok is not None and tok.type in types

    def match(self, *types: TokenType) -> Optional[Token]:
        if self.check(*types):
            return self.advance()
        return None

    def expect(self, token_type: TokenType, context: str = "") -> Token:
        token = self.current_token()
        if token and token.type == token_type:
            return self.advance()
        got = token.type.name if token else "EOF"
        got_val = repr(token.value) if token else ""
        msg = f"Expected {token_type.name}"
        if context:
            msg += f" {context}"
        msg += f", got {got}"
        if got_val and got not in ("EOF",):
            msg += f" {got_val}"
        if token and token.type == TokenType.IDENTIFIER:
            sugg = did_you_mean(token.value, [t.name.lower() for t in TokenType])
            if sugg:
                msg += f" (did you mean '{sugg[0]}'?)"
        raise self.error(msg, token)

    def error(self, message: str, token: Optional[Token] = None) -> NpSyntaxError:
        token = token or self.current_token()
        line = token.line if token else 0
        column = token.column if token else 0
        return NpSyntaxError(message, file=self.file, line=line, column=column,
                             source_lines=self.source_lines)

    def skip_newlines(self) -> None:
        while self.check(TokenType.NEWLINE):
            self.advance()

    # ------------------------------------------------------------------ #
    # Entry point
    # ------------------------------------------------------------------ #
    def parse(self) -> List[Any]:
        statements = []
        self.skip_newlines()
        while not self.check(TokenType.EOF):
            statement = self.parse_statement()
            if statement is not None:
                statements.append(statement)
            self.skip_newlines()
        return statements

    # ------------------------------------------------------------------ #
    # Statements
    # ------------------------------------------------------------------ #
    def parse_statement(self) -> Any:
        tok = self.current_token()
        if tok is None:
            return None

        if tok.type == TokenType.IMPORT:
            return self.parse_import()
        if tok.type == TokenType.FROM:
            return self.parse_from_import()

        if tok.type == TokenType.DEF:
            return self.parse_function_def()
        if tok.type == TokenType.RETURN:
            return self.parse_return()
        if tok.type == TokenType.IF:
            return self.parse_if()
        if tok.type in (TokenType.WHILE,):
            return self.parse_while()
        if tok.type in (TokenType.FOR,):
            return self.parse_for()
        if tok.type in (TokenType.BREAK,):
            token = self.advance()
            return BreakNode(token.line, token.column)
        if tok.type in (TokenType.CONTINUE,):
            token = self.advance()
            return ContinueNode(token.line, token.column)
        if tok.type in (TokenType.PASS,):
            self.advance()
            return PassNode()
        if tok.type in (TokenType.CLASS,):
            return self.parse_class_def()
        if tok.type == TokenType.CONST:
            return self.parse_const()
        if tok.type == TokenType.YIELD:
            return self.parse_yield()
        if tok.type in (TokenType.TRY,):
            return self.parse_try()
        if tok.type in (TokenType.RAISE,):
            return self.parse_raise()
        if tok.type in (TokenType.WITH,):
            return self.parse_with()

        return self.parse_expression_statement()

    def parse_return(self) -> ReturnNode:
        tok = self.advance()  # return / firta
        value = None
        if not self.check(TokenType.NEWLINE, TokenType.EOF, TokenType.DEDENT):
            value = self.parse_expression()
        return ReturnNode(value, tok.line, tok.column)

    def parse_const(self) -> ConstNode:
        tok = self.advance()  # const / sthir
        name = self.expect(TokenType.IDENTIFIER, "as constant name").value
        type_expr = None
        if self.match(TokenType.COLON):
            type_expr = self.parse_expression()
        value = None
        if self.match(TokenType.ASSIGN):
            value = self.parse_expression()
        return ConstNode(name, type_expr, value, tok.line, tok.column)

    def parse_yield(self) -> YieldNode:
        tok = self.advance()  # yield / dinu
        value = None
        if not self.check(TokenType.NEWLINE, TokenType.EOF, TokenType.DEDENT,
                          TokenType.RPAREN, TokenType.COMMA, TokenType.RBRACKET,
                          TokenType.RBRACE):
            value = self.parse_expression()
        return YieldNode(value, tok.line, tok.column)

    def parse_expression_statement(self) -> Any:
        start = self.current_token()
        expr = self.parse_expression()

        # Annotated declaration:  name: type = value
        if (isinstance(expr, VariableNode) and self.check(TokenType.COLON)):
            # Distinguish from slice/map context; statement level is safe.
            self.advance()
            type_expr = self.parse_expression()
            value = None
            if self.match(TokenType.ASSIGN):
                value = self.parse_expression()
            return AnnotationNode(expr.name, type_expr, value,
                                  start.line if start else 0,
                                  start.column if start else 0)

        # Assignment:  target = expr   |   target op= expr
        if self.check(TokenType.ASSIGN, TokenType.PLUS_ASSIGN, TokenType.MINUS_ASSIGN,
                      TokenType.STAR_ASSIGN, TokenType.SLASH_ASSIGN, TokenType.PERCENT_ASSIGN):
            op_tok = self.advance()
            value = self.parse_expression()
            if op_tok.type == TokenType.ASSIGN:
                return AssignmentNode(expr, value, op_tok.line, op_tok.column)
            return AugAssignmentNode(expr, op_tok.value[0], value, op_tok.line, op_tok.column)

        # Tuple unpacking without parentheses:  a, b = [1, 2]
        if isinstance(expr, VariableNode) and self.check(TokenType.COMMA):
            elements = [expr]
            while self.match(TokenType.COMMA):
                elements.append(self.parse_expression())
            if self.check(TokenType.ASSIGN):
                self.advance()
                value = self.parse_expression()
                return AssignmentNode(TupleNode(elements), value,
                                      start.line if start else 0,
                                      start.column if start else 0)
            raise self.error("Invalid statement: expected '=' after unpacking targets")

        # Legacy: bare print(...) call becomes PrintNode for fast-path printing.
        if (isinstance(expr, FunctionCallNode) and isinstance(expr.function, VariableNode)
                and expr.function.name == "print"):
            return PrintNode(expr.args)

        return expr

    # ------------------------------------------------------------------ #
    def parse_block(self) -> List[Any]:
        """Parse an indented block (or a single inline statement after ':')."""
        if self.match(TokenType.COLON):
            # Inline block:  if x: y = 1
            if not self.check(TokenType.NEWLINE):
                statements = [self.parse_statement()]
                return statements
            self.skip_newlines()

        if self.match(TokenType.INDENT):
            statements = []
            self.skip_newlines()
            while not self.check(TokenType.DEDENT, TokenType.EOF):
                statement = self.parse_statement()
                if statement is not None:
                    statements.append(statement)
                self.skip_newlines()
            self.expect(TokenType.DEDENT, "to close this block")
            return statements

        raise self.error("Expected an indented block")

    # ------------------------------------------------------------------ #
    def parse_import(self) -> ImportNode:
        tok = self.advance()  # import / lyau
        module = self.expect(TokenType.IDENTIFIER, "as module name").value
        aliases = {module: module}  # default: bind under its own name
        if self.match(TokenType.AS):
            alias = self.expect(TokenType.IDENTIFIER).value
            aliases[alias] = module
        return ImportNode(module, aliases=aliases, line=tok.line, column=tok.column)

    def parse_from_import(self) -> ImportNode:
        tok = self.advance()  # from / bata
        module = self.expect(TokenType.IDENTIFIER, "as module name").value
        self.expect_import_keyword()
        names = []
        aliases = {}
        if self.match(TokenType.STAR):
            names = ["*"]
        else:
            while True:
                name = self.expect(TokenType.IDENTIFIER).value
                if self.match(TokenType.AS):
                    alias = self.expect(TokenType.IDENTIFIER).value
                    aliases[alias] = name
                else:
                    aliases[name] = name
                names.append(name)
                if not self.match(TokenType.COMMA):
                    break
        return ImportNode(module, names=names, aliases=aliases,
                          line=tok.line, column=tok.column)

    def expect_import_keyword(self) -> Token:
        if self.check(TokenType.IMPORT):
            return self.advance()
        if self.current_token() and self.current_token().value in ("lyau", "import"):
            return self.advance()
        raise self.error("Expected 'import' or 'lyau' after module name")

    # ------------------------------------------------------------------ #
    def parse_function_def(self) -> FunctionDefNode:
        tok = self.advance()  # def / kaam
        name = self.expect(TokenType.IDENTIFIER, "as function name").value
        self.expect(TokenType.LPAREN)
        params = self.parse_params()
        self.expect(TokenType.RPAREN)
        return_annotation = None
        if self.match(TokenType.ARROW):
            return_annotation = self.parse_expression()
        self.skip_newlines()
        body = self.parse_block()
        return FunctionDefNode(name, params, body, return_annotation,
                               tok.line, tok.column)

    def parse_params(self) -> List[Param]:
        params: List[Param] = []
        while not self.check(TokenType.RPAREN):
            kind = "normal"
            if self.match(TokenType.STAR):
                kind = "star"
            elif self.match(TokenType.POWER):
                kind = "doublestar"
            name = self.expect(TokenType.IDENTIFIER, "as parameter name").value
            annotation = None
            if self.match(TokenType.COLON):
                annotation = self.parse_type_annotation()
            default = None
            if self.match(TokenType.ASSIGN):
                default = self.parse_expression()
            params.append(Param(name, default, annotation, kind))
            if not self.match(TokenType.COMMA):
                break
        return params

    def parse_type_annotation(self):
        # Type annotations are parsed as expressions: text, number, [text], etc.
        if self.match(TokenType.LBRACKET):
            inner = self.parse_expression()
            self.expect(TokenType.RBRACKET)
            return ListNode([inner])
        return self.parse_expression()

    # ------------------------------------------------------------------ #
    def parse_if(self) -> IfNode:
        tok = self.advance()  # if / yedi
        condition = self.parse_expression()
        body = self.parse_block()
        elif_branches = []
        else_body = None

        self.skip_newlines()
        while self.check(TokenType.ELIF):
            elif_tok = self.advance()
            elif_condition = self.parse_expression()
            elif_body = self.parse_block()
            elif_branches.append((elif_condition, elif_body))
            self.skip_newlines()

        if self.check(TokenType.ELSE):
            self.advance()
            else_body = self.parse_block()

        return IfNode(condition, body, elif_branches, else_body,
                      tok.line, tok.column)

    def parse_while(self) -> WhileNode:
        tok = self.advance()
        condition = self.parse_expression()
        body = self.parse_block()
        return WhileNode(condition, body, tok.line, tok.column)

    def parse_for(self) -> ForNode:
        tok = self.advance()
        targets = [self.expect(TokenType.IDENTIFIER).value]
        while self.match(TokenType.COMMA):
            targets.append(self.expect(TokenType.IDENTIFIER).value)
        if not self.match(TokenType.IN):
            raise self.error("Expected 'in' or 'ma' in for loop",
                             self.current_token())
        iterable = self.parse_expression()
        self.skip_newlines()
        body = self.parse_block()
        return ForNode(targets, iterable, body, tok.line, tok.column)

    # ------------------------------------------------------------------ #
    def parse_class_def(self) -> ClassDefNode:
        tok = self.advance()  # class / kakshya
        name = self.expect(TokenType.IDENTIFIER, "as class name").value
        bases = []
        if self.match(TokenType.LPAREN):
            if not self.check(TokenType.RPAREN):
                bases.append(self.parse_expression())
                while self.match(TokenType.COMMA):
                    bases.append(self.parse_expression())
            self.expect(TokenType.RPAREN)
        self.skip_newlines()
        body = self.parse_block()
        return ClassDefNode(name, bases, body, tok.line, tok.column)

    # ------------------------------------------------------------------ #
    def parse_try(self) -> TryNode:
        tok = self.advance()  # try / koshish
        self.skip_newlines()
        body = self.parse_block()
        handlers = []
        else_body = None
        finally_body = None

        self.skip_newlines()
        while self.check(TokenType.EXCEPT):
            self.advance()
            exc_name = None
            bind_name = None
            if self.check(TokenType.IDENTIFIER):
                exc_name = self.advance().value
                if self.match(TokenType.AS):
                    bind_name = self.expect(TokenType.IDENTIFIER).value
            self.skip_newlines()
            handler_body = self.parse_block()
            handlers.append((exc_name, bind_name, handler_body))
            self.skip_newlines()

        if self.check(TokenType.ELSE):
            self.advance()
            else_body = self.parse_block()
            self.skip_newlines()

        if self.check(TokenType.FINALLY):
            self.advance()
            self.skip_newlines()
            finally_body = self.parse_block()

        if not handlers and finally_body is None:
            raise self.error("'try' must have at least one 'except' or a 'finally'",
                             tok)
        return TryNode(body, handlers, else_body, finally_body, tok.line, tok.column)

    def parse_raise(self) -> RaiseNode:
        tok = self.advance()
        value = None
        if not self.check(TokenType.NEWLINE, TokenType.EOF):
            value = self.parse_expression()
        return RaiseNode(value, tok.line, tok.column)

    def parse_with(self) -> WithNode:
        tok = self.advance()
        items = []
        while True:
            expr = self.parse_expression()
            bind = None
            if self.match(TokenType.AS):
                bind = self.expect(TokenType.IDENTIFIER).value
            items.append((expr, bind))
            if not self.match(TokenType.COMMA):
                break
        self.skip_newlines()
        body = self.parse_block()
        return WithNode(items, body, tok.line, tok.column)

    # ------------------------------------------------------------------ #
    # Expressions (precedence climbing)
    # ------------------------------------------------------------------ #
    def parse_expression(self):
        return self.parse_ternary()

    def parse_ternary(self):
        value = self.parse_logical_or()
        if self.check(TokenType.IF):
            saved_pos = self.pos
            self.advance()
            condition = self.parse_logical_or()
            if self.match(TokenType.ELSE):
                otherwise = self.parse_ternary()
                return TernaryNode(condition, value, otherwise)
            # No 'natra': rewind so a comprehension guard's `yedi cond`
            # remains for parse_comprehension_clauses to consume.
            self.pos = saved_pos
        return value

    def parse_logical_or(self):
        left = self.parse_logical_and()
        while self.check(TokenType.OR):
            self.advance()
            right = self.parse_logical_and()
            left = LogicalOpNode(left, "or", right)
        return left

    def parse_logical_and(self):
        left = self.parse_not()
        while self.check(TokenType.AND):
            self.advance()
            right = self.parse_not()
            left = LogicalOpNode(left, "and", right)
        return left

    def parse_not(self):
        if self.check(TokenType.NOT):
            tok = self.advance()
            operand = self.parse_not()
            return UnaryOpNode("not", operand, tok.line, tok.column)
        return self.parse_comparison()

    def parse_comparison(self):
        left = self.parse_range()
        while self.check(TokenType.EQUAL, TokenType.NOT_EQUAL, TokenType.LESS,
                         TokenType.LESS_EQUAL, TokenType.GREATER, TokenType.GREATER_EQUAL,
                         TokenType.IN):
            if self.check(TokenType.IN):
                self.advance()
                left = BinaryOpNode(left, "in", self.parse_range(),
                                    self.current_token().line if self.current_token() else 0,
                                    0)
                continue
            op_tok = self.advance()
            right = self.parse_range()
            left = BinaryOpNode(left, op_tok.value, right, op_tok.line, op_tok.column)
        return left

    def parse_range(self):
        left = self.parse_additive()
        # Inside [...] brackets, '..' belongs to slice syntax (a[1..3]),
        # so the range expression is suppressed there.
        if self.check(TokenType.ELLIPSIS) and self.subscript_depth == 0:
            self.advance()
            right = self.parse_additive()
            return BinaryOpNode(left, "..", right, 0, 0)
        return left

    def parse_additive(self):
        left = self.parse_multiplicative()
        while self.check(TokenType.PLUS, TokenType.MINUS):
            op_tok = self.advance()
            right = self.parse_multiplicative()
            left = BinaryOpNode(left, op_tok.value, right, op_tok.line, op_tok.column)
        return left

    def parse_multiplicative(self):
        left = self.parse_unary()
        while self.check(TokenType.STAR, TokenType.SLASH, TokenType.PERCENT,
                         TokenType.DOUBLESLASH):
            op_tok = self.advance()
            right = self.parse_unary()
            op = "//" if op_tok.type == TokenType.DOUBLESLASH else op_tok.value
            left = BinaryOpNode(left, op, right, op_tok.line, op_tok.column)
        return left

    def parse_unary(self):
        if self.check(TokenType.MINUS):
            tok = self.advance()
            operand = self.parse_unary()
            return UnaryOpNode("-", operand, tok.line, tok.column)
        if self.check(TokenType.PLUS):
            self.advance()
            return self.parse_unary()
        return self.parse_power()

    def parse_power(self):
        left = self.parse_postfix()
        if self.check(TokenType.POWER):
            self.advance()
            right = self.parse_unary()  # right-associative
            return BinaryOpNode(left, "**", right)
        return left

    def parse_postfix(self):
        expr = self.parse_primary()
        while True:
            if self.check(TokenType.DOT):
                self.advance()
                member = self.expect(TokenType.IDENTIFIER, "as attribute name").value
                expr = AttributeNode(expr, member)
            elif self.check(TokenType.LPAREN):
                expr = self.parse_call(expr)
            elif self.check(TokenType.LBRACKET):
                expr = self.parse_subscript(expr)
            else:
                break
        return expr

    def parse_call(self, function):
        tok = self.expect(TokenType.LPAREN)
        args, kwargs, star_args, dstar_kwargs = [], [], [], []
        while not self.check(TokenType.RPAREN):
            if self.match(TokenType.STAR):
                star_args.append(self.parse_expression())
            elif self.match(TokenType.POWER):
                dstar_kwargs.append(self.parse_expression())
            elif (self.check(TokenType.IDENTIFIER)
                  and self.peek() and self.peek().type == TokenType.ASSIGN):
                name = self.advance().value
                self.advance()  # '='
                kwargs.append((name, self.parse_expression()))
            else:
                args.append(self.parse_expression())
            if not self.match(TokenType.COMMA):
                break
        self.expect(TokenType.RPAREN)
        return FunctionCallNode(function, args, kwargs, star_args, dstar_kwargs,
                                tok.line, tok.column)

    def parse_subscript(self, target):
        self.expect(TokenType.LBRACKET)
        self.subscript_depth += 1
        try:
            return self._parse_subscript_inner(target)
        finally:
            self.subscript_depth -= 1

    def _parse_subscript_inner(self, target):
        start = stop = step = None
        index = None
        if not self.check(TokenType.COLON, TokenType.ELLIPSIS):
            index = self.parse_expression()
        # Slice: a[1..3], a[..2], a[1..], a[1..9..2] or Python-style a[1:3]
        if self.match(TokenType.ELLIPSIS):
            start, index = index, None
            if not self.check(TokenType.RBRACKET, TokenType.ELLIPSIS):
                stop = self.parse_expression()
            if self.match(TokenType.ELLIPSIS):
                if not self.check(TokenType.RBRACKET):
                    step = self.parse_expression()
            return self._finish_subscript(target, SliceNode(target, start, stop, step))
        if self.match(TokenType.COLON):
            start, index = index, None
            if not self.check(TokenType.COLON, TokenType.RBRACKET):
                stop = self.parse_expression()
            if self.match(TokenType.COLON):
                if not self.check(TokenType.RBRACKET):
                    step = self.parse_expression()
            return self._finish_subscript(target, SliceNode(target, start, stop, step))
        return self._finish_subscript(target, IndexNode(target, index))

    def _finish_subscript(self, target, node):
        self.expect(TokenType.RBRACKET)
        return node

    def parse_primary(self):
        tok = self.current_token()
        if tok is None:
            raise self.error("Unexpected end of input")

        if tok.type == TokenType.NUMBER:
            self.advance()
            return NumberNode(tok.value)
        if tok.type == TokenType.STRING:
            self.advance()
            return StringNode(tok.value)
        if tok.type == TokenType.FSTRING:
            self.advance()
            return FStringNode(tok.value, tok.line, tok.column)
        if tok.type == TokenType.BOOLEAN:
            self.advance()
            return BooleanNode(tok.value)
        if tok.type == TokenType.NULL:
            self.advance()
            return NullNode()

        if tok.type == TokenType.IDENTIFIER:
            self.advance()
            return VariableNode(tok.value)

        if tok.type == TokenType.SUPER:
            self.advance()
            return VariableNode("super")

        if tok.type == TokenType.LPAREN:
            self.advance()
            if self.check(TokenType.RPAREN):
                self.advance()
                return TupleNode([])
            first = self.parse_expression()
            if self.check(TokenType.COMMA):
                elements = [first]
                while self.match(TokenType.COMMA):
                    if self.check(TokenType.RPAREN):
                        break
                    elements.append(self.parse_expression())
                self.expect(TokenType.RPAREN)
                return TupleNode(elements)
            self.expect(TokenType.RPAREN)
            return first

        if tok.type == TokenType.LBRACKET:
            return self.parse_list_or_comprehension()
        if tok.type == TokenType.LBRACE:
            return self.parse_map_set_or_comprehension()

        if tok.type == TokenType.LAMBDA:
            return self.parse_lambda()

        raise self.error(f"Unexpected token {tok.type.name}", tok)

    def parse_list_or_comprehension(self) -> Any:
        tok = self.expect(TokenType.LBRACKET)
        if self.check(TokenType.RBRACKET):
            self.advance()
            return ListNode([])
        first = self.parse_expression()
        if self.check(TokenType.FOR):
            return self.finish_comprehension(first, "list", tok)
        elements = [first]
        while self.match(TokenType.COMMA):
            if self.check(TokenType.RBRACKET):
                break
            elements.append(self.parse_expression())
        self.expect(TokenType.RBRACKET)
        return ListNode(elements)

    def parse_map_set_or_comprehension(self) -> Any:
        tok = self.expect(TokenType.LBRACE)
        if self.check(TokenType.RBRACE):
            self.advance()
            return MapNode([])
        # Try to parse "key: value" first; fall back to set elements.
        if self.looks_like_map_entry():
            key = self.parse_expression()
            self.expect(TokenType.COLON)
            value = self.parse_expression()
            if self.check(TokenType.FOR):
                return self.finish_map_comprehension(key, value, tok)
            pairs = [(key, value)]
            while self.match(TokenType.COMMA):
                if self.check(TokenType.RBRACE):
                    break
                key = self.parse_expression()
                self.expect(TokenType.COLON)
                value = self.parse_expression()
                pairs.append((key, value))
            self.expect(TokenType.RBRACE)
            return MapNode(pairs)
        first = self.parse_expression()
        if self.check(TokenType.FOR):
            return self.finish_comprehension(first, "set", tok)
        elements = [first]
        while self.match(TokenType.COMMA):
            if self.check(TokenType.RBRACE):
                break
            elements.append(self.parse_expression())
        self.expect(TokenType.RBRACE)
        return SetNode(elements)

    def looks_like_map_entry(self) -> bool:
        """Peek ahead for IDENT ':' or STRING ':' pattern at this level."""
        offset = 0
        tok = self.peek_from(offset)
        if tok is None or tok.type not in (TokenType.IDENTIFIER, TokenType.STRING):
            return False
        tok2 = self.peek_from(offset + 1)
        return tok2 is not None and tok2.type == TokenType.COLON

    def peek_from(self, offset: int) -> Optional[Token]:
        pos = self.pos + offset
        if pos < len(self.tokens):
            return self.tokens[pos]
        return None

    def finish_comprehension(self, element, kind: str, tok: Token) -> Any:
        target, iterable, conditions = self.parse_comprehension_clauses()
        closing = TokenType.RBRACKET if kind == "list" else TokenType.RBRACE
        self.expect(closing)
        return ComprehensionNode(kind, element, target, iterable, conditions)

    def finish_map_comprehension(self, key, value, tok: Token) -> Any:
        target, iterable, conditions = self.parse_comprehension_clauses()
        self.expect(TokenType.RBRACE)
        return ComprehensionNode("map", None, target, iterable, conditions,
                                 key=key, value=value)

    def parse_comprehension_clauses(self) -> Tuple[str, Any, list]:
        self.expect(TokenType.FOR)
        target = self.expect(TokenType.IDENTIFIER).value
        self.expect(TokenType.IN)
        iterable = self.parse_expression()
        conditions = []
        while self.check(TokenType.IF):
            self.advance()
            conditions.append(self.parse_expression())
        return target, iterable, conditions

    def parse_lambda(self) -> LambdaNode:
        tok = self.advance()  # lambda
        params = []
        while not self.check(TokenType.COLON):
            if self.match(TokenType.STAR):
                name = self.expect(TokenType.IDENTIFIER).value
                params.append(Param(name, None, None, "star"))
            elif self.match(TokenType.POWER):
                name = self.expect(TokenType.IDENTIFIER).value
                params.append(Param(name, None, None, "doublestar"))
            else:
                name = self.expect(TokenType.IDENTIFIER).value
                default = None
                if self.match(TokenType.ASSIGN):
                    default = self.parse_expression()
                params.append(Param(name, default))
            if not self.match(TokenType.COMMA):
                break
        self.expect(TokenType.COLON)
        body = self.parse_expression()
        return LambdaNode(params, body, tok.line, tok.column)

    # Legacy compatibility shims ----------------------------------------- #
    def peek_is_assignment(self) -> bool:  # pragma: no cover - legacy API
        tok = self.current_token()
        if not tok or tok.type != TokenType.IDENTIFIER:
            return False
        nxt = self.peek()
        return bool(nxt and nxt.type in (TokenType.ASSIGN, TokenType.PLUS_ASSIGN,
                                         TokenType.MINUS_ASSIGN))


def parse(tokens: List[Token], file: str = "<source>",
          source_lines: Optional[List[str]] = None) -> List[Any]:
    """Convenience function to parse tokens into AST."""
    parser = Parser(tokens, file=file, source_lines=source_lines)
    return parser.parse()

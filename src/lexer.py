"""
NepaliCode Lexer
================

Tokenizes .np source into a token stream with real INDENT/DEDENT tokens
(Python-style indentation-driven blocks), string escapes, f-strings,
template strings, and the full Nepali + English keyword set.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import List, Optional

from src.errors import NpSyntaxError, did_you_mean

__all__ = ["TokenType", "Token", "Lexer", "tokenize"]


class TokenType(Enum):
    # Literals
    NUMBER = "NUMBER"
    STRING = "STRING"
    FSTRING = "FSTRING"       # value is list of parts: str | ('expr', source)
    BOOLEAN = "BOOLEAN"
    NULL = "NULL"

    # Names
    IDENTIFIER = "IDENTIFIER"

    # Statement keywords
    IF = "IF"                 # if / yedi
    ELSE = "ELSE"             # else / natra
    ELIF = "ELIF"             # elif / athawa
    FOR = "FOR"               # for / ko_lagi
    WHILE = "WHILE"           # while / jabasamma
    DEF = "DEF"               # def / kaam
    RETURN = "RETURN"         # return / firta
    CLASS = "CLASS"           # class / kakshya
    IMPORT = "IMPORT"         # import / lyau
    FROM = "FROM"             # from / bata
    TRY = "TRY"               # try / koshish
    EXCEPT = "EXCEPT"         # except / samau
    FINALLY = "FINALLY"       # finally / antya
    RAISE = "RAISE"           # raise / uthau
    WITH = "WITH"             # with / bhitra
    IN = "IN"                 # in / ma
    IS = "IS"                 # is
    AND = "AND"               # and / ra
    OR = "OR"                 # or / wa
    NOT = "NOT"               # not / hoina
    PASS = "PASS"             # pass (no-op)
    CONST = "CONST"           # const / sthir
    YIELD = "YIELD"           # yield / dinu (generators)
    BREAK = "BREAK"           # break / rok
    CONTINUE = "CONTINUE"     # continue / agadi

    # Delimiters that need their own tokens
    ARROW = "ARROW"           # ->
    LAMBDA = "LAMBDA"         # lambda (anonymous functions)
    AS = "AS"                 # as (import alias / except capture)
    SUPER = "SUPER"           # super (parent-class access in methods)
    COLON = "COLON"
    COMMA = "COMMA"
    DOT = "DOT"
    ELLIPSIS = "ELLIPSIS"     # .. (slice)

    # Assignment
    ASSIGN = "ASSIGN"
    PLUS_ASSIGN = "PLUS_ASSIGN"
    MINUS_ASSIGN = "MINUS_ASSIGN"
    STAR_ASSIGN = "STAR_ASSIGN"
    SLASH_ASSIGN = "SLASH_ASSIGN"
    PERCENT_ASSIGN = "PERCENT_ASSIGN"

    # Operators
    PLUS = "PLUS"
    MINUS = "MINUS"
    STAR = "STAR"
    DOUBLESTAR = "DOUBLESTAR"
    SLASH = "SLASH"
    DOUBLESLASH = "DOUBLESLASH"
    PERCENT = "PERCENT"
    POWER = "POWER"           # alias of DOUBLESTAR kept for old tests
    EQUAL = "EQUAL"
    NOT_EQUAL = "NOT_EQUAL"
    LESS = "LESS"
    LESS_EQUAL = "LESS_EQUAL"
    GREATER = "GREATER"
    GREATER_EQUAL = "GREATER_EQUAL"

    # Boolean/null (kept so older tooling can pattern-match)
    TRUE = "TRUE"
    FALSE = "FALSE"
    NONE = "NONE"

    # Delimiters
    LPAREN = "LPAREN"
    RPAREN = "RPAREN"
    LBRACE = "LBRACE"
    RBRACE = "RBRACE"
    LBRACKET = "LBRACKET"
    RBRACKET = "RBRACKET"

    # Layout
    NEWLINE = "NEWLINE"
    INDENT = "INDENT"
    DEDENT = "DEDENT"
    EOF = "EOF"


# Keywords: English and Nepali aliases map to the same token types.
KEYWORDS = {
    # English
    "if": TokenType.IF,
    "else": TokenType.ELSE,
    "elif": TokenType.ELIF,
    "for": TokenType.FOR,
    "while": TokenType.WHILE,
    "def": TokenType.DEF,
    "return": TokenType.RETURN,
    "class": TokenType.CLASS,
    "import": TokenType.IMPORT,
    "from": TokenType.FROM,
    "try": TokenType.TRY,
    "except": TokenType.EXCEPT,
    "finally": TokenType.FINALLY,
    "raise": TokenType.RAISE,
    "with": TokenType.WITH,
    "in": TokenType.IN,
    "is": TokenType.IS,
    "and": TokenType.AND,
    "or": TokenType.OR,
    "not": TokenType.NOT,
    "pass": TokenType.PASS,
    "const": TokenType.CONST,
    "sthir": TokenType.CONST,
    "yield": TokenType.YIELD,
    "dinu": TokenType.YIELD,
    "break": TokenType.BREAK,
    "continue": TokenType.CONTINUE,
    "lambda": TokenType.LAMBDA,
    "as": TokenType.AS,
    "super": TokenType.SUPER,
    "True": TokenType.TRUE,
    "False": TokenType.FALSE,
    "None": TokenType.NONE,
    # Nepali
    "yedi": TokenType.IF,
    "natra": TokenType.ELSE,
    "athawa": TokenType.ELIF,       # per spec: athawa = elif
    "natabhaye": TokenType.ELIF,    # legacy alias kept for compatibility
    "ko_lagi": TokenType.FOR,
    "jabasamma": TokenType.WHILE,
    "kaam": TokenType.DEF,
    "firta": TokenType.RETURN,
    "kakshya": TokenType.CLASS,
    "lyau": TokenType.IMPORT,
    "bata": TokenType.FROM,
    "koshish": TokenType.TRY,
    "samau": TokenType.EXCEPT,
    "antya": TokenType.FINALLY,
    "uthau": TokenType.RAISE,
    "bhitra": TokenType.WITH,
    "ma": TokenType.IN,
    "ra": TokenType.AND,
    "wa": TokenType.OR,
    "hoina": TokenType.NOT,
    "rok": TokenType.BREAK,
    "agadi": TokenType.CONTINUE,
    "sacho": TokenType.TRUE,
    "jhut": TokenType.FALSE,
    "khali": TokenType.NONE,
    # Legacy lowercase literals kept for backward compatibility with
    # existing .np programs (true/false/none/null).
    "true": TokenType.TRUE,
    "false": TokenType.FALSE,
    "none": TokenType.NONE,
    "null": TokenType.NONE,
}

# Kept for compatibility with the old lexer API.
_TRUE_VALUES = {"true", "sacho", "True", "Sacho"}
_FALSE_VALUES = {"false", "jhut", "False", "Jhut"}
_NULL_VALUES = {"none", "null", "khali", "None", "Khali"}


@dataclass
class Token:
    type: TokenType
    value: object
    line: int
    column: int

    def __repr__(self) -> str:  # pragma: no cover - debug helper
        return f"Token({self.type.name}, {self.value!r}, {self.line}:{self.column})"


class Lexer:
    def __init__(self, source: str, file: str = "<source>") -> None:
        self.source = source
        self.file = file
        self.pos = 0
        self.line = 1
        self.column = 1
        self.tokens: List[Token] = []
        # Indentation stack: level -> list of column positions on that level.
        # Multi-column alignment (tabs expanded to 4) is supported like Python.
        self.indents: List[int] = [0]
        # Bracket depth: no NEWLINE/INDENT/DEDENT inside (...) [...] {...}
        self.paren_depth = 0
        # True at the start of a logical line (used for INDENT handling).
        self.at_line_start = True

    # ------------------------------------------------------------------ #
    # Low-level helpers
    # ------------------------------------------------------------------ #
    def current_char(self) -> Optional[str]:
        if self.pos < len(self.source):
            return self.source[self.pos]
        return None

    def advance(self) -> str:
        char = self.source[self.pos]
        self.pos += 1
        if char == "\n":
            self.line += 1
            self.column = 1
        else:
            self.column += 1
        return char

    def peek(self, offset: int = 1) -> Optional[str]:
        peek_pos = self.pos + offset
        if peek_pos < len(self.source):
            return self.source[peek_pos]
        return None

    def _error(self, message: str, line: int, column: int,
               suggestion_word: Optional[str] = None) -> NpSyntaxError:
        lines = self.source.splitlines()
        kwargs = {}
        if suggestion_word:
            words = set(KEYWORDS.keys())
            sugg = did_you_mean(suggestion_word, sorted(words))
            if sugg:
                kwargs["suggestions"] = sugg
        return NpSyntaxError(message, file=self.file, line=line, column=column,
                             source_lines=lines, **kwargs)

    # ------------------------------------------------------------------ #
    # Lexing
    # ------------------------------------------------------------------ #
    def tokenize(self) -> List[Token]:
        while self.pos < len(self.source):
            char = self.current_char()

            # --- Indentation at the start of a logical line ---------------
            # Runs whether or not the line begins with whitespace: a line
            # starting at column 1 after an indented block must emit DEDENT.
            if self.at_line_start and self.paren_depth == 0:
                start_line, start_col = self.line, self.column
                width = 0
                while self.current_char() and self.current_char() in " \t":
                    ch = self.advance()
                    width += 4 if ch == "\t" else 1
                self._handle_indent_width(width, start_line, start_col)
                self.at_line_start = False
                continue

            self.at_line_start = False

            # --- Blank lines and comments --------------------------------
            if char == "\n":
                if self.paren_depth == 0 and self.tokens and self.tokens[-1].type not in (
                    TokenType.NEWLINE, TokenType.INDENT, TokenType.DEDENT
                ):
                    self.tokens.append(Token(TokenType.NEWLINE, "\n", self.line, self.column))
                self.advance()
                self.at_line_start = True
                continue

            if char in " \t\r":
                self.advance()
                continue

            if char == "#":
                while self.current_char() and self.current_char() != "\n":
                    self.advance()
                continue

            line, column = self.line, self.column

            # --- Numbers --------------------------------------------------
            if char.isdigit():
                self._read_number(line, column)
                continue

            # --- Strings / f-strings -------------------------------------
            # f"..." / f'...': consume the f/F prefix together with the quote.
            if char in "fF" and self.peek() in "\"'":
                self.advance()  # skip the f prefix
                self._read_string(self.current_char(), prefix="f", line=line, column=column)
                continue
            if char in "\"'":
                self._read_string(char, prefix="", line=line, column=column)
                continue

            # --- Identifiers / keywords ----------------------------------
            if char.isalpha() or char == "_" or ord(char) > 127:
                identifier = self._read_identifier()
                token_type = KEYWORDS.get(identifier)
                if token_type == TokenType.TRUE:
                    self.tokens.append(Token(TokenType.BOOLEAN, True, line, column))
                elif token_type == TokenType.FALSE:
                    self.tokens.append(Token(TokenType.BOOLEAN, False, line, column))
                elif token_type == TokenType.NONE:
                    self.tokens.append(Token(TokenType.NULL, None, line, column))
                elif token_type is not None:
                    self.tokens.append(Token(token_type, identifier, line, column))
                else:
                    self.tokens.append(Token(TokenType.IDENTIFIER, identifier, line, column))
                continue

            # --- Operators and delimiters --------------------------------
            if char == "+":
                self._two_char("=", TokenType.PLUS_ASSIGN, TokenType.PLUS, line, column)
                continue
            if char == "-":
                if self.peek() == ">":
                    self.advance(); self.advance()
                    self.tokens.append(Token(TokenType.ARROW, "->", line, column))
                elif self.peek() == "=":
                    self.advance(); self.advance()
                    self.tokens.append(Token(TokenType.MINUS_ASSIGN, "-=", line, column))
                else:
                    self.tokens.append(Token(TokenType.MINUS, "-", line, column))
                    self.advance()
                continue
            if char == "*":
                if self.peek() == "*":
                    self.advance(); self.advance()
                    self.tokens.append(Token(TokenType.POWER, "**", line, column))
                elif self.peek() == "=":
                    self.advance(); self.advance()
                    self.tokens.append(Token(TokenType.STAR_ASSIGN, "*=", line, column))
                else:
                    self.tokens.append(Token(TokenType.STAR, "*", line, column))
                    self.advance()
                continue
            if char == "/":
                if self.peek() == "/":
                    self.advance(); self.advance()
                    self.tokens.append(Token(TokenType.DOUBLESLASH, "//", line, column))
                elif self.peek() == "=":
                    self.advance(); self.advance()
                    self.tokens.append(Token(TokenType.SLASH_ASSIGN, "/=", line, column))
                else:
                    self.tokens.append(Token(TokenType.SLASH, "/", line, column))
                    self.advance()
                continue
            if char == "%":
                self._two_char("=", TokenType.PERCENT_ASSIGN, TokenType.PERCENT, line, column)
                continue
            if char == "=":
                self._two_char("=", TokenType.EQUAL, TokenType.ASSIGN, line, column)
                continue
            if char == "!":
                if self.peek() == "=":
                    self.advance(); self.advance()
                    self.tokens.append(Token(TokenType.NOT_EQUAL, "!=", line, column))
                    continue
                raise self._error("Unexpected character '!'. Use '!=' for inequality.",
                                  line, column)
            if char == "<":
                self._two_char("=", TokenType.LESS_EQUAL, TokenType.LESS, line, column)
                continue
            if char == ">":
                self._two_char("=", TokenType.GREATER_EQUAL, TokenType.GREATER, line, column)
                continue

            # --- Brackets --------------------------------------------------
            if char == "(":
                self.paren_depth += 1
                self.tokens.append(Token(TokenType.LPAREN, "(", line, column))
                self.advance()
                continue
            if char == ")":
                self.paren_depth = max(0, self.paren_depth - 1)
                self.tokens.append(Token(TokenType.RPAREN, ")", line, column))
                self.advance()
                continue
            if char == "[":
                self.paren_depth += 1
                self.tokens.append(Token(TokenType.LBRACKET, "[", line, column))
                self.advance()
                continue
            if char == "]":
                self.paren_depth = max(0, self.paren_depth - 1)
                self.tokens.append(Token(TokenType.RBRACKET, "]", line, column))
                self.advance()
                continue
            if char == "{":
                self.paren_depth += 1
                self.tokens.append(Token(TokenType.LBRACE, "{", line, column))
                self.advance()
                continue
            if char == "}":
                self.paren_depth = max(0, self.paren_depth - 1)
                self.tokens.append(Token(TokenType.RBRACE, "}", line, column))
                self.advance()
                continue

            if char == ":":
                self.tokens.append(Token(TokenType.COLON, ":", line, column))
                self.advance()
                continue
            if char == ",":
                self.tokens.append(Token(TokenType.COMMA, ",", line, column))
                self.advance()
                continue
            if char == ".":
                if self.peek() == ".":
                    self.advance(); self.advance()
                    self.tokens.append(Token(TokenType.ELLIPSIS, "..", line, column))
                else:
                    self.tokens.append(Token(TokenType.DOT, ".", line, column))
                    self.advance()
                continue

            raise self._error(f"Unexpected character {char!r}", line, column)

        # Flush trailing newline and close all open indentation levels.
        if self.tokens and self.tokens[-1].type not in (
            TokenType.NEWLINE, TokenType.INDENT, TokenType.DEDENT
        ):
            self.tokens.append(Token(TokenType.NEWLINE, "\n", self.line, self.column))
        while len(self.indents) > 1:
            self.indents.pop()
            self.tokens.append(Token(TokenType.DEDENT, None, self.line, self.column))
        self.tokens.append(Token(TokenType.EOF, None, self.line, self.column))
        return self.tokens

    # ------------------------------------------------------------------ #
    def _handle_indent_width(self, width: int, start_line: int, start_col: int) -> None:
        """Emit INDENT/DEDENT tokens for the given indentation width."""
        # Blank line or comment-only line: no layout tokens.
        ch = self.current_char()
        if ch is None or ch == "\n" or ch == "#":
            return

        current = self.indents[-1]
        if width > current:
            self.indents.append(width)
            self.tokens.append(Token(TokenType.INDENT, width, start_line, start_col))
        elif width < current:
            while self.indents and self.indents[-1] > width:
                self.indents.pop()
                self.tokens.append(Token(TokenType.DEDENT, None, start_line, start_col))
            if not self.indents or self.indents[-1] != width:
                raise self._error("Inconsistent indentation: unindent does not match "
                                  "any outer level", start_line, start_col)
        # width == current: nothing to emit

    def _two_char(self, second: str, pair_type: TokenType, single_type: TokenType,
                  line: int, column: int) -> None:
        if self.peek() == second:
            self.advance(); self.advance()
            self.tokens.append(Token(pair_type, f"{self.source[self.pos - 2:self.pos]}", line, column))
        else:
            self.tokens.append(Token(single_type, self.current_char(), line, column))
            self.advance()

    def _read_number(self, line: int, column: int) -> None:
        result = ""
        while self.current_char() and self.current_char().isdigit():
            result += self.advance()
        if self.current_char() == "." and self.peek() and self.peek().isdigit():
            result += self.advance()  # the dot
            while self.current_char() and self.current_char().isdigit():
                result += self.advance()
            self.tokens.append(Token(TokenType.NUMBER, float(result), line, column))
        else:
            self.tokens.append(Token(TokenType.NUMBER, int(result), line, column))

    def _read_string(self, quote: str, prefix: str,
                     line: int, column: int) -> None:
        # Triple-quoted strings
        if self.peek() == quote and self.peek(2) == quote:
            self.advance(); self.advance(); self.advance()
            return self._read_triple_string(quote, prefix, line, column)

        self.advance()  # skip opening quote
        raw = ""
        while True:
            ch = self.current_char()
            if ch is None or ch == "\n":
                raise self._error("Unterminated string literal", line, column)
            if ch == quote:
                self.advance()
                break
            if ch == "\\":
                self.advance()
                raw += self._read_escape(line, column)
            else:
                raw += self.advance()

        if prefix == "f":
            parts = _parse_fstring_body(raw, self.file, line, column)
            self.tokens.append(Token(TokenType.FSTRING, parts, line, column))
        else:
            self.tokens.append(Token(TokenType.STRING, raw, line, column))

    def _read_triple_string(self, quote: str, prefix: str,
                            line: int, column: int) -> None:
        raw = ""
        while True:
            ch = self.current_char()
            if ch is None:
                raise self._error("Unterminated triple-quoted string", line, column)
            if ch == quote and self.peek() == quote and self.peek(2) == quote:
                self.advance(); self.advance(); self.advance()
                break
            if ch == "\\":
                self.advance()
                raw += self._read_escape(line, column)
            else:
                raw += self.advance()
        if prefix == "f":
            parts = _parse_fstring_body(raw, self.file, line, column)
            self.tokens.append(Token(TokenType.FSTRING, parts, line, column))
        else:
            self.tokens.append(Token(TokenType.STRING, raw, line, column))

    def _read_escape(self, line: int, column: int) -> str:
        ch = self.current_char()
        if ch is None:
            raise self._error("Unterminated escape sequence", line, column)
        self.advance()
        mapping = {
            "n": "\n", "t": "\t", "r": "\r", "0": "\0", "b": "\b",
            "f": "\f", "v": "\v", "a": "\a", "'": "'", '"': '"',
            "\\": "\\", "`": "`",
        }
        if ch in mapping:
            return mapping[ch]
        if ch == "x" and self.current_char() is not None:
            hex_digits = ""
            while len(hex_digits) < 2 and self.current_char() and \
                    self.current_char() in "0123456789abcdefABCDEF":
                hex_digits += self.advance()
            if hex_digits:
                return chr(int(hex_digits, 16))
        return "\\" + ch

    def _read_identifier(self) -> str:
        result = ""
        while self.current_char() and (self.current_char().isalnum() or
                                       self.current_char() == "_" or
                                       ord(self.current_char()) > 127):
            result += self.advance()
        return result


# ---------------------------------------------------------------------- #
# f-string support
# ---------------------------------------------------------------------- #
def _parse_fstring_body(raw: str, file: str, line: int, column: int):
    """Split f-string body into literal text and ('expr', source) parts."""
    parts = []
    buf = ""
    i = 0
    while i < len(raw):
        ch = raw[i]
        if ch == "{":
            if i + 1 < len(raw) and raw[i + 1] == "{":
                buf += "{"
                i += 2
                continue
            depth = 1
            j = i + 1
            expr = ""
            while j < len(raw) and depth > 0:
                if raw[j] == "{":
                    depth += 1
                elif raw[j] == "}":
                    depth -= 1
                    if depth == 0:
                        break
                expr += raw[j]
                j += 1
            if depth != 0:
                raise NpSyntaxError("Unterminated '{' in f-string", file=file,
                                    line=line, column=column)
            if buf:
                parts.append(buf)
                buf = ""
            parts.append(("expr", expr.strip()))
            i = j + 1
            continue
        if ch == "}" and i + 1 < len(raw) and raw[i + 1] == "}":
            buf += "}"
            i += 2
            continue
        buf += ch
        i += 1
    if buf:
        parts.append(buf)
    return parts


def tokenize(source: str, file: str = "<source>") -> List[Token]:
    """Convenience function to tokenize source code."""
    lexer = Lexer(source, file=file)
    return lexer.tokenize()

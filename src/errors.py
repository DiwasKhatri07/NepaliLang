"""
NepaliCode Diagnostics
======================

NP-coded errors with file, line, column, source context and
"did you mean" suggestions, matching the language spec:

    NP1007 Unknown Name

    main.np:8:5

    Name 'broser' is not defined.

    Did you mean:
        browser
"""

from __future__ import annotations

from typing import List, Optional, Sequence

__all__ = [
    "NpError",
    "NpSyntaxError",
    "NpNameError",
    "NpTypeError",
    "NpValueError",
    "NpZeroDivisionError",
    "NpIndexError",
    "NpKeyError",
    "NpAttributeError",
    "NpImportError",
    "NpStopIteration",
    "format_location",
    "levenshtein",
    "did_you_mean",
    "suggest_names",
]


class NpError(Exception):
    """Base error for all NepaliCode diagnostics."""

    code: str = "NP0000"
    title: str = "Error"

    def __init__(self, message: str = "", *, file: str = "<unknown>",
                 line: int = 0, column: int = 0,
                 source_lines: Optional[Sequence[str]] = None,
                 suggestions: Optional[Sequence[str]] = None) -> None:
        self.message = message
        self.file = file
        self.line = line
        self.column = column
        self.source_lines = list(source_lines) if source_lines is not None else None
        self.suggestions = list(suggestions) if suggestions else []
        super().__init__(self.render())

    # ------------------------------------------------------------------ #
    def with_location(self, file: str, line: int, column: int,
                      source_lines: Optional[Sequence[str]] = None) -> "NpError":
        """Fill in location information (used by the pipeline as errors bubble up)."""
        if self.line == 0:
            self.file = file
            self.line = line
            self.column = column
            if source_lines is not None and self.source_lines is None:
                self.source_lines = list(source_lines)
        return self

    def render(self) -> str:
        parts: List[str] = []
        header = f"{self.code} {self.title}"
        if self.message:
            header += f"\n\n{self.message}"
        parts.append(header)
        parts.append(format_location(self.file, self.line, self.column))
        snippet = self._snippet()
        if snippet:
            parts.append(snippet)
        if self.suggestions:
            parts.append("Did you mean:")
            for name in self.suggestions[:3]:
                parts.append(f"    {name}")
        return "\n".join(parts)

    def _snippet(self) -> str:
        if not self.source_lines or self.line <= 0:
            return ""
        idx = self.line - 1
        if idx < 0 or idx >= len(self.source_lines):
            return ""
        out = []
        width = len(str(self.line))
        out.append(f"  {self.line:>{width}} | {self.source_lines[idx]}")
        caret_pad = " " * max(self.column - 1, 0)
        out.append(f"  {' ' * width} | {caret_pad}^")
        if idx > 0:
            out.insert(0, f"  {self.line - 1:>{width}} | {self.source_lines[idx - 1]}")
        if idx + 1 < len(self.source_lines):
            out.append(f"  {self.line + 1:>{width}} | {self.source_lines[idx + 1]}")
        return "\n".join(out)


class NpSyntaxError(NpError):
    code = "NP1001"
    title = "Syntax Error"


class NpNameError(NpError):
    code = "NP1007"
    title = "Unknown Name"


class NpTypeError(NpError):
    code = "NP2001"
    title = "Type Error"


class NpValueError(NpError):
    code = "NP2002"
    title = "Value Error"


class NpZeroDivisionError(NpError):
    code = "NP2003"
    title = "Division by Zero"


class NpIndexError(NpError):
    code = "NP2004"
    title = "Index Error"


class NpKeyError(NpError):
    code = "NP2005"
    title = "Key Error"


class NpAttributeError(NpError):
    code = "NP2006"
    title = "Attribute Error"


class NpImportError(NpError):
    code = "NP1008"
    title = "Import Error"


class NpStopIteration(Exception):
    """Internal: raised by exhausted iterators (never shown to users)."""


# ---------------------------------------------------------------------- #
def format_location(file: str, line: int, column: int) -> str:
    if line <= 0:
        return file
    if column <= 0:
        return f"{file}:{line}"
    return f"{file}:{line}:{column}"


def levenshtein(a: str, b: str) -> int:
    """Classic edit distance, O(len(a) * len(b)) with two rows."""
    if a == b:
        return 0
    if not a:
        return len(b)
    if not b:
        return len(a)
    prev = list(range(len(b) + 1))
    for i, ca in enumerate(a, 1):
        cur = [i]
        for j, cb in enumerate(b, 1):
            cur.append(min(prev[j] + 1, cur[j - 1] + 1, prev[j - 1] + (ca != cb)))
        prev = cur
    return prev[-1]


def did_you_mean(word: str, candidates: Sequence[str], max_distance: int = 3) -> List[str]:
    """Return candidates close to `word`, best first. Empty when nothing is close."""
    scored = []
    for cand in candidates:
        if cand == word:
            continue
        dist = levenshtein(word.lower(), cand.lower())
        # Allow longer distances for longer words.
        threshold = min(max_distance, max(2, len(word) // 2 + 1))
        if dist <= threshold:
            scored.append((dist, cand))
    scored.sort(key=lambda pair: (pair[0], pair[1]))
    return [cand for _, cand in scored]

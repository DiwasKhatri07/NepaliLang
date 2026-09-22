"""
Tests for the NepaliCode Lexer
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.lexer import tokenize, TokenType


def test_numbers():
    tokens = tokenize("42")
    assert tokens[0].type == TokenType.NUMBER
    assert tokens[0].value == 42


def test_floats():
    tokens = tokenize("3.5")
    assert tokens[0].type == TokenType.NUMBER
    assert tokens[0].value == 3.5


def test_strings():
    tokens = tokenize('"Hello"')
    assert tokens[0].type == TokenType.STRING
    assert tokens[0].value == "Hello"


def test_string_escapes():
    tokens = tokenize(r'"a\nb\tc"')
    assert tokens[0].value == "a\nb\tc"


def test_identifiers():
    tokens = tokenize("variable")
    assert tokens[0].type == TokenType.IDENTIFIER


def test_keywords():
    tokens = tokenize("if else for while")
    types = [t.type for t in tokens[:4]]
    assert types == [TokenType.IF, TokenType.ELSE, TokenType.FOR, TokenType.WHILE]


def test_nepali_keywords():
    tokens = tokenize("yedi natra athawa ko_lagi jabasamma")
    types = [t.type for t in tokens[:5]]
    assert types == [TokenType.IF, TokenType.ELSE, TokenType.ELIF,
                     TokenType.FOR, TokenType.WHILE]


def test_operators():
    tokens = tokenize("+ - * / % **")
    types = [t.type for t in tokens[:6]]
    assert types == [TokenType.PLUS, TokenType.MINUS, TokenType.STAR,
                     TokenType.SLASH, TokenType.PERCENT, TokenType.POWER]


def test_augmented_assignment():
    tokens = tokenize("x += 1")
    assert tokens[1].type == TokenType.PLUS_ASSIGN


def test_arrow():
    tokens = tokenize("kaam f() -> number")
    assert any(t.type == TokenType.ARROW for t in tokens)


def test_booleans():
    tokens = tokenize("sacho jhut true false")
    values = [t.value for t in tokens[:4]]
    assert values == [True, False, True, False]
    assert all(t.type == TokenType.BOOLEAN for t in tokens[:4])


def test_null():
    tokens = tokenize("khali")
    assert tokens[0].type == TokenType.NULL
    assert tokens[0].value is None


def test_comments():
    tokens = tokenize("42 # this is a comment")
    assert tokens[0].type == TokenType.NUMBER
    assert all(t.type != TokenType.STRING for t in tokens)


def test_indent_dedent():
    source = "yedi a:\n    x = 1\n    y = 2\nz = 3\n"
    tokens = tokenize(source)
    types = [t.type for t in tokens]
    assert TokenType.INDENT in types
    assert TokenType.DEDENT in types
    # INDENT comes before the first body statement, DEDENT before z
    assert types.index(TokenType.INDENT) < types.index(TokenType.DEDENT)


def test_multiple_dedents():
    source = "if a:\n    if b:\n        x = 1\ny = 2\n"
    tokens = tokenize(source)
    dedents = [t for t in tokens if t.type == TokenType.DEDENT]
    assert len(dedents) == 2


def test_fstring_tokens():
    tokens = tokenize('f"Namaste {name}"')
    assert tokens[0].type == TokenType.FSTRING
    parts = tokens[0].value
    assert parts[0] == "Namaste "
    assert parts[1] == ("expr", "name")


def test_slice_colon():
    tokens = tokenize("a[1:3]")
    types = [t.type for t in tokens]
    assert TokenType.COLON in types


def test_unicode_identifiers():
    tokens = tokenize("नाम = 5")
    assert tokens[0].type == TokenType.IDENTIFIER
    assert tokens[0].value == "नाम"


def run_all_tests():
    print("Running Lexer Tests...")
    tests = [test_numbers, test_floats, test_strings, test_string_escapes,
             test_identifiers, test_keywords, test_nepali_keywords,
             test_operators, test_augmented_assignment, test_arrow,
             test_booleans, test_null, test_comments, test_indent_dedent,
             test_multiple_dedents, test_fstring_tokens, test_slice_colon,
             test_unicode_identifiers]
    passed = 0
    failed = 0
    for test in tests:
        try:
            test()
            print(f"[PASS] {test.__name__}")
            passed += 1
        except AssertionError as e:
            print(f"[FAIL] {test.__name__}: {e}")
            failed += 1
        except Exception as e:
            print(f"[ERROR] {test.__name__}: {type(e).__name__}: {e}")
            failed += 1
    print(f"\n{passed}/{len(tests)} lexer tests passed")
    return failed == 0


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)

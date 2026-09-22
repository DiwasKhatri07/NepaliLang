"""
Tests for the NepaliCode Parser
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.lexer import tokenize
from src.parser import parse, PrintNode
from src.errors import NpSyntaxError


def _parse(src):
    return parse(tokenize(src))


def test_basic_expression():
    assert len(_parse("3 + 4")) == 1


def test_variable_assignment():
    assert len(_parse("x = 42")) == 1


def test_function_call():
    ast = _parse("print(42)")
    assert isinstance(ast[0], PrintNode)


def test_if_statement():
    assert len(_parse("if x > 0:\n    print(x)")) == 1


def test_for_loop():
    assert len(_parse("for i in 10:\n    print(i)")) == 1


def test_function_definition():
    assert len(_parse("def test():\n    return 42")) == 1


def test_list_literal():
    assert len(_parse("[1, 2, 3]")) == 1


def test_map_literal():
    assert len(_parse('{"name": "Diwas"}')) == 1


def test_block_not_swallowed():
    """The classic bug: a block must not eat the statements after it."""
    ast = _parse("if a:\n    b = 1\nc = 2\nd = 3")
    assert len(ast) == 3  # if, c, d


def test_function_body_full():
    ast = _parse("kaam f():\n    a = 1\n    b = 2\n    firta a + b\nx = f()")
    assert len(ast) == 2
    fn = ast[0]
    assert len(fn.body) == 3


def test_nested_blocks():
    ast = _parse("yedi a:\n    yedi b:\n        x = 1\n    y = 2\nz = 3")
    assert len(ast) == 2
    outer = ast[0]
    assert len(outer.body) == 2  # inner if + y = 2


def test_else_if_chain():
    src = "yedi a:\n    x = 1\nathawa b:\n    x = 2\nnatra:\n    x = 3"
    ast = _parse(src)
    assert len(ast) == 1
    assert len(ast[0].elif_branches) == 1
    assert ast[0].else_body is not None


def test_break_continue():
    ast = _parse("jabasamma a:\n    rok\n")
    assert ast[0].body[0].__class__.__name__ == "BreakNode"
    ast = _parse("jabasamma a:\n    agadi\n")
    assert ast[0].body[0].__class__.__name__ == "ContinueNode"


def test_try_except_finally():
    src = "koshish:\n    x = 1\nsamau e:\n    y = 2\nantya:\n    z = 3"
    ast = _parse(src)
    node = ast[0]
    assert node.__class__.__name__ == "TryNode"
    assert len(node.handlers) == 1
    assert node.finally_body is not None


def test_class_def():
    src = 'kakshya User:\n    kaam greet(self):\n        firta "hi"'
    ast = _parse(src)
    assert ast[0].__class__.__name__ == "ClassDefNode"
    assert ast[0].name == "User"


def test_class_inheritance():
    ast = _parse("kakshya Dog(Animal):\n    pass")
    assert ast[0].bases and ast[0].bases[0].name == "Animal"


def test_lambda():
    ast = _parse("f = lambda x: x * 2")
    assert ast[0].value.__class__.__name__ == "LambdaNode"


def test_comprehension():
    ast = _parse("squares = [i * i for i ma items]")
    assert ast[0].value.__class__.__name__ == "ComprehensionNode"


def test_comprehension_with_guard():
    ast = _parse("evens = [x for x ma items yedi x % 2 == 0]")
    comp = ast[0].value
    assert len(comp.conditions) == 1


def test_ternary():
    ast = _parse('x = "a" yedi b natra "c"')
    assert ast[0].value.__class__.__name__ == "TernaryNode"


def test_kwargs_call():
    ast = _parse('greet(name="Diwas", greeting="Hajur")')
    call = ast[0]
    assert call.kwargs and call.kwargs[0][0] == "name"


def test_star_args_params():
    ast = _parse("kaam f(*args, **kwargs):\n    pass")
    kinds = [p.kind for p in ast[0].params]
    assert kinds == ["star", "doublestar"]


def test_annotations():
    src = "kaam multiply(a: number, b: number) -> number:\n    firta a * b"
    ast = _parse(src)
    fn = ast[0]
    assert fn.return_annotation is not None
    assert fn.params[0].annotation is not None


def test_slice():
    ast = _parse("b = items[1..3]")
    assert ast[0].value.__class__.__name__ == "SliceNode"


def test_attribute_assignment():
    ast = _parse("self.name = value")
    assert ast[0].target.__class__.__name__ == "AttributeNode"


def test_index_assignment():
    ast = _parse('d["key"] = value')
    assert ast[0].target.__class__.__name__ == "IndexNode"


def test_import_aliases():
    ast = _parse("bata ganit lyau sqrt, power")
    node = ast[0]
    assert node.module == "ganit"
    assert "sqrt" in node.aliases


def test_logical_operators():
    ast = _parse("x = a ra b wa hoina c")
    assert ast[0].value.__class__.__name__ == "LogicalOpNode"


def test_range_expression():
    ast = _parse("for i ma 1..5:\n    print(i)")
    assert ast[0].iterable.operator == ".."


def test_const():
    ast = _parse("sthir PI = 3.14")
    assert ast[0].__class__.__name__ == "ConstNode"


def test_syntax_error_location():
    try:
        _parse("kaam f(:\n    pass")
        assert False, "expected NpSyntaxError"
    except NpSyntaxError as e:
        assert "NP1001" in str(e)


def run_all_tests():
    print("Running Parser Tests...")
    tests = [v for k, v in sorted(globals().items()) if k.startswith("test_")]
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
    print(f"\n{passed}/{len(tests)} parser tests passed")
    return failed == 0


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)

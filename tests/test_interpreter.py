"""
Tests for the NepaliCode Interpreter
"""

import io
import os
import sys
from contextlib import redirect_stdout

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.interpreter import Interpreter
from src.errors import NpError, NpNameError, NpTypeError


def run(src):
    """Run source and capture printed output."""
    buffer = io.StringIO()
    with redirect_stdout(buffer):
        Interpreter().run_source(src)
    return buffer.getvalue()


def run_result(src):
    """Run source and return the value of the last expression statement."""
    return Interpreter().run_source(src)


def test_arithmetic():
    assert run_result("3 + 4") == 7


def test_precedence():
    assert run_result("2 + 3 * 4") == 14
    assert run_result("2 ** 3 ** 2") == 512


def test_variables():
    interp = Interpreter()
    interp.run_source("x = 42")
    assert interp.globals.get("x")[1] == 42


def test_functions():
    out = run("def add(a, b):\n    return a + b\nprint(add(3, 4))")
    assert out.strip() == "7"


def test_nepali_function():
    out = run("kaam jod(a, b):\n    firta a + b\nprint(jod(10, 20))")
    assert out.strip() == "30"


def test_default_arguments():
    out = run('kaam greet(n, g="Namaste"):\n    firta g + " " + n\n'
              'print(greet("Diwas"))')
    assert out.strip() == "Namaste Diwas"


def test_keyword_arguments():
    out = run('kaam greet(n, g="Namaste"):\n    firta g + " " + n\n'
              'print(greet("Diwas", g="Hajur"))')
    assert out.strip() == "Hajur Diwas"


def test_star_args_kwargs():
    out = run("kaam f(*args, **kwargs):\n    firta len(args) + len(kwargs)\n"
              "print(f(1, 2, x=3))")
    assert out.strip() == "3"


def test_closures():
    out = run("kaam make_counter():\n"
              "    count = 0\n"
              "    kaam inc():\n"
              "        count += 1\n"
              "        firta count\n"
              "    firta inc\n"
              "c = make_counter()\n"
              "c()\n"
              "print(c())")
    assert out.strip() == "2"


def test_recursion():
    out = run("kaam fact(n):\n"
              "    yedi n <= 1:\n"
              "        firta 1\n"
              "    firta n * fact(n - 1)\n"
              "print(fact(5))")
    assert out.strip() == "120"


def test_lambda():
    out = run("double = lambda x: x * 2\nprint(double(21))")
    assert out.strip() == "42"


def test_booleans():
    assert run_result("sacho") is True
    assert run_result("jhut") is False


def test_string_concat():
    assert run_result('"Hello" + " " + "World"') == "Hello World"


def test_string_methods():
    out = run('print("namaste".upper())')
    assert out.strip() == "NAMASTE"


def test_lists():
    out = run("items = [1, 2, 3]\nitems.append(4)\nprint(items)")
    assert out.strip() == "[1, 2, 3, 4]"


def test_list_indexing_and_slicing():
    out = run("items = [10, 20, 30, 40]\nprint(items[2])\nprint(items[1..3])")
    assert out.split() == ["30", "[20, 30]"]


def test_maps():
    out = run('d = {"a": 1}\nd["b"] = 2\nprint(d["b"])')
    assert out.strip() == "2"


def test_map_methods():
    out = run('d = {"a": 1, "b": 2}\nprint(d.get("z", 99))')
    assert out.strip() == "99"


def test_comparison():
    assert run_result("5 > 3") is True


def test_logical_operators():
    assert run_result("sacho ra jhut") is False
    assert run_result("sacho wa jhut") is True
    assert run_result("hoina jhut") is True


def test_if_elif_else():
    out = run("a = 5\nyedi a < 3:\n    print('sano')\n"
              "athawa a == 5:\n    print('five')\nnatra:\n    print('thulo')")
    assert out.strip() == "five"


def test_while_break():
    out = run("i = 0\njabasamma sacho:\n    i += 1\n    yedi i >= 3:\n        rok\nprint(i)")
    assert out.strip() == "3"


def test_for_continue():
    out = run("t = 0\nfor i ma 1..5:\n    yedi i == 3:\n        agadi\n    t += i\nprint(t)")
    assert out.strip() == "12"


def test_for_over_list():
    out = run("t = 0\nfor x ma [10, 20, 30]:\n    t += x\nprint(t)")
    assert out.strip() == "60"


def test_fstring():
    out = run('name = "Diwas"\nage = 21\nprint(f"{name} ra {age}")')
    assert out.strip() == "Diwas ra 21"


def test_fstring_expression():
    out = run("x = 4\nprint(f\"doubled: {x * 2}\")")
    assert out.strip() == "doubled: 8"


def test_classes():
    out = run('kakshya Animal:\n'
              '    kaam __init__(self, name):\n'
              '        self.name = name\n'
              '    kaam speak(self):\n'
              '        firta self.name + " awaaz"\n'
              'a = Animal("Kalu")\n'
              'print(a.speak())')
    assert out.strip() == "Kalu awaaz"


def test_inheritance_super():
    out = run('kakshya A:\n'
              '    kaam hi(self):\n'
              '        firta "A"\n'
              'kakshya B(A):\n'
              '    kaam hi(self):\n'
              '        firta super.hi(self) + "B"\n'
              'print(B().hi())')
    assert out.strip() == "AB"


def test_operator_overloading():
    out = run('kakshya V:\n'
              '    kaam __init__(self, x):\n'
              '        self.x = x\n'
              '    kaam __add__(self, other):\n'
              '        firta V(self.x + other.x)\n'
              '    kaam __str__(self):\n'
              '        firta f"V({self.x})"\n'
              'print(V(1) + V(2))')
    assert out.strip() == "V(3)"


def test_try_except_finally():
    out = run('koshish:\n'
              '    uthau "custom problem"\n'
              'samau e:\n'
              '    print("caught " + e.message)\n'
              'antya:\n'
              '    print("antya")')
    assert out.split() == ["caught", "custom", "problem", "antya"]


def test_division_by_zero_caught():
    out = run("koshish:\n    x = 1 / 0\nsamau ZeroDivisionError:\n    print('caught')")
    assert out.strip() == "caught"


def test_uncaught_exception_raises_np_error():
    try:
        run('uthau "boom"')
        assert False, "expected NpError"
    except NpError:
        pass


def test_comprehensions():
    out = run("print([i * 2 for i ma 1..5])")
    assert out.strip() == "[2, 4, 6, 8, 10]"


def test_comprehension_guard():
    out = run("print([x for x ma 1..10 yedi x % 2 == 0])")
    assert out.strip() == "[2, 4, 6, 8, 10]"


def test_ternary():
    out = run('print("barabar" yedi 5 == 5 natra "farak")')
    assert out.strip() == "barabar"


def test_unpacking():
    out = run("a, b = [1, 2]\nprint(a + b)")
    assert out.strip() == "3"


def test_const_protection():
    out = run("sthir PI = 3.14\nkoshish:\n    PI = 3\nsamau e:\n    print('protected')")
    assert out.strip() == "protected"


def test_annotations():
    out = run("kaam multiply(a: number, b: number) -> number:\n"
              "    firta a * b\nprint(multiply(6, 7))")
    assert out.strip() == "42"


def test_generator():
    out = run("kaam counting(n):\n"
              "    i = 0\n"
              "    jabasamma i < n:\n"
              "        dinu i\n"
              "        i += 1\n"
              "t = 0\n"
              "for x ma counting(4):\n"
              "    t += x\n"
              "print(t)")
    assert out.strip() == "6"


def test_module_import():
    out = run("lyau ganit\nprint(ganit.sqrt(16))")
    assert out.strip() == "4.0"


def test_from_import():
    out = run("bata ganit lyau sqrt\nprint(sqrt(25))")
    assert out.strip() == "5.0"


def test_unknown_name_suggestion():
    try:
        run("broser = 1\nprint(browser)")
        assert False, "expected NpNameError"
    except NpNameError as e:
        assert "broser" in str(e)


def test_error_has_location():
    try:
        run("x = 1\nyedi x >\n    pass")
        assert False, "expected NpError"
    except NpError as e:
        assert "NP" in str(e)


def test_with_statement():
    out = run('kakshya Ctx:\n'
              '    kaam __enter__(self):\n'
              '        print("enter")\n'
              '        firta self\n'
              '    kaam __exit__(self):\n'
              '        print("exit")\n'
              'bhitra Ctx():\n'
              '    print("inside")')
    assert out.split() == ["enter", "inside", "exit"]


def test_value_methods_map():
    out = run("items = [1, 2, 3]\nprint(items.map(lambda x: x * 10))")
    assert out.strip() == "[10, 20, 30]"


def test_len_of_string():
    assert run_result('len("namaste")') == 7


def run_all_tests():
    print("Running Interpreter Tests...")
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
            import traceback
            print(f"[ERROR] {test.__name__}: {type(e).__name__}: {e}")
            traceback.print_exc()
            failed += 1
    print(f"\n{passed}/{len(tests)} interpreter tests passed")
    return failed == 0


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)

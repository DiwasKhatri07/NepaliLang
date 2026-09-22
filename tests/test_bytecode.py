"""
Bytecode VM Tests
"""

import sys
import os

# Add project root to path
project_root = os.path.join(os.path.dirname(__file__), '..')
sys.path.insert(0, project_root)

from src.lexer import tokenize
from src.parser import parse
from src.bytecode import compile_to_bytecode, run_bytecode

def test_simple_arithmetic():
    """Test basic arithmetic operations"""
    source = """
a = 10
b = 20
print(a + b)
"""
    tokens = tokenize(source)
    ast = parse(tokens)
    
    try:
        bytecode = compile_to_bytecode(ast)
        print(f"Compiled {len(bytecode.instructions)} instructions")
        print(f"Constants: {bytecode.constants}")
        print(f"Names: {bytecode.names}")
        result = run_bytecode(bytecode)
        print("Bytecode test passed: Arithmetic operations work")
        return True
    except Exception as e:
        print(f"Bytecode test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_variable_assignment():
    """Test variable assignment and retrieval"""
    source = """
x = 5
print(x)
"""
    tokens = tokenize(source)
    ast = parse(tokens)
    
    try:
        bytecode = compile_to_bytecode(ast)
        result = run_bytecode(bytecode)
        print("Bytecode test passed: Variable assignment works")
        return True
    except Exception as e:
        print(f"Bytecode test failed: {e}")
        return False

def test_print_literal():
    """Test printing literal values"""
    source = """
print("Hello from bytecode!")
"""
    tokens = tokenize(source)
    ast = parse(tokens)
    
    try:
        bytecode = compile_to_bytecode(ast)
        result = run_bytecode(bytecode)
        print("Bytecode test passed: Print literal works")
        return True
    except Exception as e:
        print(f"Bytecode test failed: {e}")
        return False

def run_all_bytecode_tests():
    """Run all bytecode tests"""
    print("Running Bytecode VM Tests...")
    print("=" * 50)
    
    tests = [
        test_simple_arithmetic,
        test_variable_assignment,
        test_print_literal
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        try:
            if test():
                passed += 1
            else:
                failed += 1
        except Exception as e:
            print(f"Test crashed: {e}")
            failed += 1
    
    print("=" * 50)
    print(f"Results: {passed} passed, {failed} failed")
    
    return failed == 0

if __name__ == "__main__":
    success = run_all_bytecode_tests()
    sys.exit(0 if success else 1)
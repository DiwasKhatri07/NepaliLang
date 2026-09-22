"""
Run all NepaliLang tests
"""

import sys
import os
import io

# Set UTF-8 encoding for stdout
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import subprocess

def run_test_file(test_file):
    """Run a single test file."""
    print(f"\nRunning {test_file}...")
    result = subprocess.run([sys.executable, test_file], cwd=os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    return result.returncode == 0

def main():
    """Run all tests."""
    print("=" * 50)
    print("NepaliLang Test Suite")
    print("=" * 50)
    
    test_files = [
        "tests/test_lexer.py",
        "tests/test_parser.py", 
        "tests/test_interpreter.py"
    ]
    
    results = {}
    for test_file in test_files:
        results[test_file] = run_test_file(test_file)
    
    print("\n" + "=" * 50)
    print("Test Summary")
    print("=" * 50)
    
    passed = sum(1 for result in results.values() if result)
    total = len(results)
    
    for test_file, result in results.items():
        status = "[PASS]" if result else "[FAIL]"
        print(f"{status} {test_file}")
    
    print(f"\nTotal: {passed}/{total} test suites passed")
    
    return all(results.values())

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
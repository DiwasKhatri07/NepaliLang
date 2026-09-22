"""
Test module for module system integration
"""

def hello():
    return "Hello from test module!"

def add(a, b):
    return a + b

_module_dict = {
    'hello': hello,
    'add': add,
}
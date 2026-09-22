"""
NepaliCode JSON Library
Enhanced JSON operations with file helpers
"""

import json
from typing import Any, Dict, Optional


def parse(text: str) -> Any:
    """Parse JSON string to Python object."""
    return json.loads(text)


def stringify(data: Any, indent: int = 2) -> str:
    """Convert Python object to JSON string."""
    return json.dumps(data, indent=indent, ensure_ascii=False)


def load_file(filename: str) -> Any:
    """Read JSON from file."""
    with open(filename, 'r', encoding='utf-8') as f:
        return json.load(f)


def save_file(filename: str, data: Any, indent: int = 2) -> None:
    """Write data to JSON file."""
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=indent, ensure_ascii=False)


# Aliases for compatibility
read = load_file
write = save_file


# For interpreter context
_module_dict = {
    'parse': parse,
    'stringify': stringify,
    'load_file': load_file,
    'save_file': save_file,
    'read': read,
    'write': write,
}
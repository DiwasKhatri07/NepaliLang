"""
NepaliCode File Library
Comprehensive file operations
"""

import os
import shutil
from typing import List, Optional
from pathlib import Path


def write(filename: str, content: str, mode: str = 'w') -> None:
    """Write content to file."""
    with open(filename, mode, encoding='utf-8') as f:
        f.write(content)


def read(filename: str) -> str:
    """Read content from file."""
    with open(filename, 'r', encoding='utf-8') as f:
        return f.read()


def append(filename: str, content: str) -> None:
    """Append content to file."""
    write(filename, content, mode='a')


def exists(filename: str) -> bool:
    """Check if file exists."""
    return os.path.exists(filename)


def delete(filename: str) -> None:
    """Delete file."""
    os.remove(filename)


def copy(source: str, target: str) -> None:
    """Copy file."""
    shutil.copy(source, target)


def move(source: str, target: str) -> None:
    """Move file."""
    shutil.move(source, target)


def list_files(directory: str = '.') -> List[str]:
    """List files in directory."""
    return os.listdir(directory)


def mkdir(directory: str) -> None:
    """Create directory."""
    os.makedirs(directory, exist_ok=True)


def rmdir(directory: str) -> None:
    """Remove directory."""
    shutil.rmtree(directory)


def get_size(filename: str) -> int:
    """Get file size in bytes."""
    return os.path.getsize(filename)


def get_mtime(filename: str) -> float:
    """Get file modification time."""
    return os.path.getmtime(filename)


def is_file(filename: str) -> bool:
    """Check if path is a file."""
    return os.path.isfile(filename)


def is_directory(filename: str) -> bool:
    """Check if path is a directory."""
    return os.path.isdir(filename)


def join(*paths: str) -> str:
    """Join path components."""
    return os.path.join(*paths)


def abspath(path: str) -> str:
    """Get absolute path."""
    return os.path.abspath(path)


def dirname(path: str) -> str:
    """Get directory name."""
    return os.path.dirname(path)


def basename(path: str) -> str:
    """Get base name."""
    return os.path.basename(path)


def read_lines(filename: str) -> List[str]:
    """Read file as list of lines."""
    with open(filename, 'r', encoding='utf-8') as f:
        return f.readlines()


def write_lines(filename: str, lines: List[str]) -> None:
    """Write list of lines to file."""
    with open(filename, 'w', encoding='utf-8') as f:
        f.writelines(lines)


# For interpreter context
_module_dict = {
    'write': write,
    'read': read,
    'append': append,
    'exists': exists,
    'delete': delete,
    'copy': copy,
    'move': move,
    'list_files': list_files,
    'mkdir': mkdir,
    'rmdir': rmdir,
    'get_size': get_size,
    'get_mtime': get_mtime,
    'is_file': is_file,
    'is_directory': is_directory,
    'join': join,
    'abspath': abspath,
    'dirname': dirname,
    'basename': basename,
    'read_lines': read_lines,
    'write_lines': write_lines,
}
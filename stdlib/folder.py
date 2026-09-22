"""
NepaliLang Standard Library - Folder
Provides folder operations.
"""

import os

def create(path):
    """Create folder."""
    os.makedirs(path, exist_ok=True)

def exists(path):
    """Check if folder exists."""
    return os.path.exists(path) and os.path.isdir(path)

def list(path):
    """List files in folder."""
    return os.listdir(path)

def delete(path):
    """Delete folder."""
    import shutil
    shutil.rmtree(path)
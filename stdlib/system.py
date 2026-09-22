"""
NepaliLang Standard Library - System
Provides system information.
"""

import platform
import os

def os_name():
    """Get operating system name."""
    return platform.system()

def platform_name():
    """Get platform name."""
    return platform.platform()

def hostname():
    """Get hostname."""
    return platform.node()

def username():
    """Get current username."""
    return os.getlogin()
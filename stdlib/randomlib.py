"""
NepaliLang Standard Library - Random
Provides random number generation.
"""

import random

def number(min_val, max_val):
    """Get random number between min and max."""
    return random.randint(min_val, max_val)

def choice(items):
    """Get random choice from list."""
    return random.choice(items)

def shuffle(items):
    """Shuffle list in place."""
    random.shuffle(items)
    return items
"""
Simple Python wrapper that handles path issues
"""

import sys
import os

# Add current directory to path
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

# Import and run main
from main import main

if __name__ == "__main__":
    main()
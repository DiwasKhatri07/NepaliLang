"""
NepaliLang Main Entry Point (legacy module form)
================================================

Kept for backward compatibility: older scripts run `python src/nepali.py ...`.
All functionality now lives in src/cli.py.
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.cli import main  # noqa: E402

if __name__ == "__main__":
    sys.exit(main())

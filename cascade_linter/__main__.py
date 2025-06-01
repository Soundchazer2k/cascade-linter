#!/usr/bin/env python3
"""
Cascade Linter - Main entry point for CLI execution

This module enables running the cascade linter as:
    python -m cascade_linter

It provides a convenient entry point to the CLI interface.
"""

import sys
from cascade_linter.cli import main

if __name__ == "__main__":
    sys.exit(main())

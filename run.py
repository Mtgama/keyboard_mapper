#!/usr/bin/env python3
"""Entry point for Keyboard Layout Mapper."""

import sys
from pathlib import Path

# Add src directory to Python path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from keyboard_layout_mapper.main import main

if __name__ == "__main__":
    raise SystemExit(main())

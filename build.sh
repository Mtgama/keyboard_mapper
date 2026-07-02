#!/bin/bash
# Build script for Keyboard Layout Mapper

set -e

echo "Building Keyboard Layout Mapper..."

# Clean previous builds
rm -rf build dist

# Build binary
PYTHONPATH=src python -m PyInstaller \
    --onefile \
    --noconsole \
    --name changekeyboard \
    --icon=assets/icons8-keyboard-96.ico \
    --add-data "assets/icons8-keyboard-96.png:assets" \
    --add-data "assets/icons8-keyboard-96.ico:assets" \
    run.py

echo ""
echo "Build complete! Binary at: dist/changekeyboard"
echo ""
echo "To install system-wide:"
echo "  cp dist/changekeyboard ~/.local/bin/changekeyboard"
echo "  chmod +x ~/.local/bin/changekeyboard"

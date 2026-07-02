"""Basic tests for keyboard layout mapper."""

import sys
import os

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from keyboard_layout_mapper.mapper import map_text, EN_TO_FA, FA_TO_EN


def test_english_to_persian():
    """Test English to Persian conversion."""
    result = map_text("sghl")
    assert result == "سلام", f"Expected 'سلام', got '{result}'"


def test_persian_to_english():
    """Test Persian to English conversion."""
    result = map_text("سلام")
    assert result == "sghl", f"Expected 'sghl', got '{result}'"


def test_mixed_text():
    """Test mixed text conversion."""
    result = map_text("sghl و سلام")
    assert "سلام" in result or "sghl" in result


def test_numbers():
    """Test number conversion."""
    result = map_text("123")
    assert result == "۱۲۳", f"Expected '۱۲۳', got '{result}'"


def test_passthrough():
    """Test that unknown characters pass through."""
    result = map_text("hello@#$")
    assert "@" in result and "#" in result


if __name__ == "__main__":
    test_english_to_persian()
    test_persian_to_english()
    test_mixed_text()
    test_numbers()
    test_passthrough()
    print("All tests passed!")

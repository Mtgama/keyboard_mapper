"""Keyboard shortcut injection via xdotool or pynput."""

import shutil
import subprocess

try:
    from pynput import keyboard as pynput_keyboard
except Exception:
    pynput_keyboard = None


def send_shortcut(key: str) -> bool:
    """Send a keyboard shortcut to the system.

    Tries xdotool first, falls back to pynput.
    """
    if _run_xdotool(key):
        return True
    if pynput_keyboard is None:
        return False

    controller = pynput_keyboard.Controller()
    control = pynput_keyboard.Key.ctrl
    letter = key.split("+")[-1]
    controller.press(control)
    controller.press(letter)
    controller.release(letter)
    controller.release(control)
    return True


def _run_xdotool(*keys: str) -> bool:
    """Run xdotool key command."""
    if not shutil.which("xdotool"):
        return False
    try:
        subprocess.run(["xdotool", "key", "--clearmodifiers", *keys], check=True)
        return True
    except Exception:
        return False

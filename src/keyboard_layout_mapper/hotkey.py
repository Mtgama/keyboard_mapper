"""Hotkey listener service using X11 or pynput."""

import os
import threading
from PyQt6.QtCore import QObject, pyqtSignal

try:
    from pynput import keyboard as pynput_keyboard
except Exception:
    pynput_keyboard = None

try:
    from Xlib import X, XK, display
    from Xlib.error import BadAccess, DisplayConnectionError, XError
except Exception:
    X = None
    XK = None
    display = None
    BadAccess = DisplayConnectionError = XError = Exception


def parse_hotkey(hotkey: str) -> tuple[int, str]:
    """Parse hotkey string into X11 modifiers and key token."""
    modifiers = 0
    key_token = ""
    for part in hotkey.split("+"):
        token = part.strip().lower()
        if token in {"<ctrl>", "<ctrl_l>", "<ctrl_r>"}:
            modifiers |= X.ControlMask
        elif token in {"<shift>", "<shift_l>", "<shift_r>"}:
            modifiers |= X.ShiftMask
        elif token in {"<alt>", "<alt_l>", "<alt_r>"}:
            modifiers |= X.Mod1Mask
        elif token in {"<cmd>", "<super>", "<super_l>", "<super_r>"}:
            modifiers |= X.Mod4Mask
        elif token:
            key_token = token
    return modifiers, key_token


def hotkey_token_to_keysym(key_token: str) -> int:
    """Convert hotkey token to X11 keysym."""
    if len(key_token) == 1:
        return XK.string_to_keysym(key_token)

    normalized = key_token.strip("<>")
    keysyms = {
        "space": "space",
        "tab": "Tab",
        "enter": "Return",
        "return": "Return",
        "esc": "Escape",
        "escape": "Escape",
        "backspace": "BackSpace",
        "delete": "Delete",
        "insert": "Insert",
        "home": "Home",
        "end": "End",
        "page_up": "Page_Up",
        "page_down": "Page_Down",
        "left": "Left",
        "right": "Right",
        "up": "Up",
        "down": "Down",
    }
    if normalized.startswith("f") and normalized[1:].isdigit():
        keysyms[normalized] = normalized.upper()
    return XK.string_to_keysym(keysyms.get(normalized, normalized))


class X11HotkeyListener(threading.Thread):
    """Global hotkey listener using X11."""

    def __init__(self, hotkey: str, on_activate, on_status) -> None:
        super().__init__(daemon=True)
        self.hotkey = hotkey
        self.on_activate = on_activate
        self.on_status = on_status
        self.running = True
        self.display = None
        self.root = None
        self.grab_errors = []

    def run(self) -> None:
        try:
            self.display = display.Display()
            self.display.set_error_handler(self.handle_x_error)
            self.root = self.display.screen().root
            modifiers, key_token = parse_hotkey(self.hotkey)
            keysym = hotkey_token_to_keysym(key_token)
            keycode = self.display.keysym_to_keycode(keysym)
            if not keycode:
                self.on_status(f"کلید شورتکات X11 قابل تشخیص نیست: {self.hotkey}")
                return

            old_stderr = os.dup(2)
            devnull = os.open(os.devnull, os.O_WRONLY)
            os.dup2(devnull, 2)
            try:
                for ignored_modifiers in (0, X.LockMask, X.Mod2Mask, X.LockMask | X.Mod2Mask):
                    self.root.grab_key(
                        keycode,
                        modifiers | ignored_modifiers,
                        owner_events=True,
                        pointer_mode=X.GrabModeAsync,
                        keyboard_mode=X.GrabModeAsync,
                    )
                self.display.flush()
                self.display.sync()
            finally:
                os.dup2(old_stderr, 2)
                os.close(old_stderr)
                os.close(devnull)

            if self.grab_errors:
                self.on_status("این شورتکات قبلاً توسط سیستم یا برنامه دیگری گرفته شده است.")
                return
            self.on_status(f"شورتکات سراسری X11 فعال است: {self.hotkey}")

            while self.running:
                event = self.display.next_event()
                if event.type == X.KeyPress:
                    self.on_activate()
        except BadAccess:
            self.on_status("این شورتکات قبلاً توسط برنامه یا سیستم دیگری گرفته شده است.")
        except (DisplayConnectionError, XError) as error:
            self.on_status(f"فعال‌سازی شورتکات X11 ناموفق بود: {error}")
        except Exception as error:
            self.on_status(f"فعال‌سازی شورتکات X11 ناموفق بود: {error}")
            return
        finally:
            self.close_display()

    def handle_x_error(self, error, request) -> None:
        if isinstance(error, BadAccess):
            self.grab_errors.append(error)
            return
        self.on_status(f"خطای X11: {error}")

    def stop(self) -> None:
        self.running = False
        self.close_display()

    def close_display(self) -> None:
        if self.display is not None:
            try:
                self.display.close()
            except Exception:
                pass
            self.display = None


class HotkeyService(QObject):
    """High-level hotkey service that manages global hotkey activation."""
    activated = pyqtSignal()
    status_changed = pyqtSignal(str)

    def __init__(self) -> None:
        super().__init__()
        self.listener = None

    def start(self, hotkey: str) -> None:
        self.stop()
        if X is not None and os.environ.get("XDG_SESSION_TYPE", "").lower() != "wayland":
            self.listener = X11HotkeyListener(hotkey, self.activated.emit, self.status_changed.emit)
            self.listener.start()
            return

        if pynput_keyboard is None:
            self.status_changed.emit("pynput نصب نیست؛ شورتکات سراسری فعال نشد.")
            return
        try:
            self.listener = pynput_keyboard.GlobalHotKeys({hotkey: self.activated.emit})
            self.listener.start()
            self.status_changed.emit(f"شورتکات فعال است: {hotkey}")
        except Exception as error:
            self.listener = None
            self.status_changed.emit(f"فعال‌سازی شورتکات ناموفق بود: {error}")

    def stop(self) -> None:
        if self.listener is not None:
            try:
                self.listener.stop()
            except Exception:
                pass
            self.listener = None

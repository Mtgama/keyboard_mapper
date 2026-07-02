"""Qt key event handling for hotkey recording."""

from PyQt6.QtCore import Qt


def qt_key_to_hotkey_token(key: int) -> str:
    """Convert Qt key code to hotkey token string."""
    if Qt.Key.Key_A <= key <= Qt.Key.Key_Z:
        return chr(ord("a") + key - Qt.Key.Key_A)
    if Qt.Key.Key_0 <= key <= Qt.Key.Key_9:
        return chr(ord("0") + key - Qt.Key.Key_0)
    if Qt.Key.Key_F1 <= key <= Qt.Key.Key_F24:
        return f"<f{key - Qt.Key.Key_F1 + 1}>"

    special_keys = {
        Qt.Key.Key_Space: "<space>",
        Qt.Key.Key_Tab: "<tab>",
        Qt.Key.Key_Return: "<enter>",
        Qt.Key.Key_Enter: "<enter>",
        Qt.Key.Key_Escape: "<esc>",
        Qt.Key.Key_Backspace: "<backspace>",
        Qt.Key.Key_Delete: "<delete>",
        Qt.Key.Key_Insert: "<insert>",
        Qt.Key.Key_Home: "<home>",
        Qt.Key.Key_End: "<end>",
        Qt.Key.Key_PageUp: "<page_up>",
        Qt.Key.Key_PageDown: "<page_down>",
        Qt.Key.Key_Left: "<left>",
        Qt.Key.Key_Right: "<right>",
        Qt.Key.Key_Up: "<up>",
        Qt.Key.Key_Down: "<down>",
    }
    return special_keys.get(Qt.Key(key), "")


def event_to_hotkey(event) -> str:
    """Convert Qt key event to hotkey string."""
    modifiers = event.modifiers()
    parts = []
    if modifiers & Qt.KeyboardModifier.ControlModifier:
        parts.append("<ctrl>")
    if modifiers & Qt.KeyboardModifier.AltModifier:
        parts.append("<alt>")
    if modifiers & Qt.KeyboardModifier.ShiftModifier:
        parts.append("<shift>")
    if modifiers & Qt.KeyboardModifier.MetaModifier:
        parts.append("<cmd>")

    key = event.key()
    if key in {
        Qt.Key.Key_Control,
        Qt.Key.Key_Shift,
        Qt.Key.Key_Alt,
        Qt.Key.Key_Meta,
        Qt.Key.Key_AltGr,
    }:
        return ""

    key_token = qt_key_to_hotkey_token(key)
    if not key_token:
        text = event.text()
        if len(text) == 1 and text.isprintable():
            key_token = text.lower()
    if not key_token:
        return ""

    parts.append(key_token)
    return "+".join(parts)

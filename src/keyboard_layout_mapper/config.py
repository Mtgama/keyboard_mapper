"""Configuration management for Keyboard Layout Mapper."""

import json
from pathlib import Path

CONFIG_DIR = Path.home() / ".config" / "keyboard-layout-mapper"
CONFIG_FILE = CONFIG_DIR / "config.json"
AUTOSTART_DIR = Path.home() / ".config" / "autostart"
AUTOSTART_DESKTOP = AUTOSTART_DIR / "keyboard-layout-mapper.desktop"
DEFAULT_HOTKEY = "<ctrl>+<shift>+l"


def load_config() -> dict:
    """Load configuration from file, with defaults."""
    defaults = {
        "hotkey": DEFAULT_HOTKEY,
        "mode": "selection",
        "restore_clipboard": True,
        "autostart": _is_autostart_enabled(),
    }
    try:
        if CONFIG_FILE.exists():
            defaults.update(json.loads(CONFIG_FILE.read_text(encoding="utf-8")))
    except Exception:
        pass
    return defaults


def save_config(config: dict) -> None:
    """Save configuration to file."""
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    CONFIG_FILE.write_text(json.dumps(config, ensure_ascii=False, indent=2), encoding="utf-8")


def set_autostart(enabled: bool) -> None:
    """Enable or disable autostart on system login."""
    AUTOSTART_DIR.mkdir(parents=True, exist_ok=True)
    exec_path = Path.home() / ".local/bin" / "changekeyboard"
    if enabled:
        AUTOSTART_DESKTOP.write_text(
            f"""[Desktop Entry]
Type=Application
Name=Keyboard Layout Mapper
Exec={exec_path} --minimized
Hidden=false
NoDisplay=false
Terminal=false
StartupNotify=false
X-GNOME-Autostart-enabled=true
Comment=Keyboard layout converter hotkey service
""",
            encoding="utf-8",
        )
    else:
        if AUTOSTART_DESKTOP.exists():
            AUTOSTART_DESKTOP.unlink()


def _is_autostart_enabled() -> bool:
    """Check if autostart is enabled."""
    return AUTOSTART_DESKTOP.exists()

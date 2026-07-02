"""Main entry point for Keyboard Layout Mapper."""

import sys
from argparse import ArgumentParser

from PyQt6.QtCore import QTimer
from PyQt6.QtGui import QGuiApplication
from PyQt6.QtWidgets import QApplication

from .config import load_config
from .mapper import map_text
from .input_sender import send_shortcut
from .ui import MainWindow


def run_once() -> int:
    """Convert focused text once and exit."""
    app = QApplication(sys.argv[:1])
    app.setQuitOnLastWindowClosed(True)
    config = load_config()

    clipboard = QGuiApplication.clipboard()
    old_clipboard_text = clipboard.text()
    if config["mode"] == "field":
        send_shortcut("ctrl+a")
        import time
        time.sleep(0.08)
    send_shortcut("ctrl+c")

    QTimer.singleShot(180, lambda: _replace_and_exit(config, old_clipboard_text))
    return app.exec()


def _replace_and_exit(config: dict, old_clipboard_text: str) -> None:
    clipboard = QGuiApplication.clipboard()
    text = clipboard.text()
    if text:
        converted_text = map_text(text)
        clipboard.setText(converted_text)
        send_shortcut("ctrl+v")
        if config.get("restore_clipboard"):
            QTimer.singleShot(700, lambda: clipboard.setText(old_clipboard_text))
    QTimer.singleShot(1200, QApplication.quit)


def main() -> int:
    parser = ArgumentParser(description="Keyboard Layout Mapper")
    parser.add_argument(
        "--convert-focused",
        action="store_true",
        help="Convert selected/focused text once and exit.",
    )
    parser.add_argument(
        "--minimized",
        action="store_true",
        help="Start minimized to system tray (used by autostart).",
    )
    args = parser.parse_args()

    if args.convert_focused:
        return run_once()

    app = QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(False)
    window = MainWindow(start_minimized=args.minimized)
    if not args.minimized:
        window.show()
    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())

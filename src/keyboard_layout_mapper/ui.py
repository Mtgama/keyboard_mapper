"""Main window UI for Keyboard Layout Mapper."""

from pathlib import Path

from PyQt6.QtCore import QEvent, Qt, QTimer
from PyQt6.QtGui import QAction, QIcon
from PyQt6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QFormLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMainWindow,
    QPushButton,
    QSystemTrayIcon,
    QTextEdit,
    QVBoxLayout,
    QWidget,
    QMenu,
)

from .config import DEFAULT_HOTKEY, load_config, save_config, set_autostart
from .hotkey import HotkeyService
from .input_handler import event_to_hotkey
from .mapper import map_text

ICON_DIR = Path(__file__).resolve().parent.parent.parent / "assets"


class MainWindow(QMainWindow):
    """Main application window."""

    def __init__(self, start_minimized: bool = False) -> None:
        super().__init__()
        self.config = load_config()
        self.hotkey_service = HotkeyService()
        self.hotkey_service.activated.connect(self.transform_focused_text)
        self.hotkey_service.status_changed.connect(self.set_status)
        self.old_clipboard_text = ""
        self.is_recording_hotkey = False
        self.start_minimized = start_minimized

        self.setWindowTitle("Keyboard Layout Mapper")
        self.setWindowIcon(QIcon(str(ICON_DIR / "icons8-keyboard-96.png")))
        self.setMinimumSize(520, 450)
        self.resize(560, 480)

        self._build_ui()
        self.tray = self._create_tray()
        self.hotkey_service.start(self.config["hotkey"])
        self.installEventFilter(self)

        if start_minimized:
            QTimer.singleShot(0, self.hide)

    def _build_ui(self) -> None:
        central = QWidget()
        self.setCentralWidget(central)

        self.hotkey_input = QLineEdit(self.config["hotkey"])
        self.hotkey_input.setReadOnly(True)
        self.record_button = QPushButton("ضبط شورتکات")
        self.record_button.clicked.connect(self.start_hotkey_recording)

        self.mode_input = QComboBox()
        self.mode_input.addItem("فقط متن انتخاب‌شده", "selection")
        self.mode_input.addItem("کل کادر فعال با Ctrl+A", "field")
        self.mode_input.setCurrentIndex(0 if self.config["mode"] == "selection" else 1)

        self.restore_clipboard = QCheckBox("بعد از تبدیل، کلیپ‌بورد قبلی برگردانده شود")
        self.restore_clipboard.setChecked(bool(self.config["restore_clipboard"]))

        self.autostart_checkbox = QCheckBox("شروع خودکار هنگام ورود به سیستم")
        self.autostart_checkbox.setChecked(bool(self.config.get("autostart", False)))

        self.status_label = QLabel()

        self.preview_input = QTextEdit("sghl و سلام را اینجا امتحان کنید.")
        self.preview_output = QTextEdit()
        self.preview_output.setReadOnly(True)

        save_button = QPushButton("ذخیره و فعال‌سازی شورتکات")
        save_button.clicked.connect(self.save_settings)
        preview_button = QPushButton("تست نگاشت")
        preview_button.clicked.connect(self.update_preview)

        hotkey_layout = QHBoxLayout()
        hotkey_layout.addWidget(self.hotkey_input)
        hotkey_layout.addWidget(self.record_button)

        form = QFormLayout()
        form.addRow("شورتکات:", hotkey_layout)
        form.addRow("حالت تبدیل:", self.mode_input)
        form.addRow("", self.restore_clipboard)
        form.addRow("", self.autostart_checkbox)

        buttons = QHBoxLayout()
        buttons.addWidget(save_button)
        buttons.addWidget(preview_button)

        layout = QVBoxLayout()
        layout.addWidget(QLabel("برای تغییر شورتکات، روی «ضبط شورتکات» بزنید و کلیدها را فشار دهید."))
        layout.addLayout(form)
        layout.addLayout(buttons)
        layout.addWidget(QLabel("متن تست:"))
        layout.addWidget(self.preview_input)
        layout.addWidget(QLabel("نتیجه:"))
        layout.addWidget(self.preview_output)
        layout.addWidget(self.status_label)

        central.setLayout(layout)
        self.update_preview()

    def eventFilter(self, watched, event) -> bool:
        if self.is_recording_hotkey and event.type() == QEvent.Type.KeyPress:
            if event.key() == Qt.Key.Key_Escape:
                self.stop_hotkey_recording(cancelled=True)
                return True

            hotkey = event_to_hotkey(event)
            if not hotkey:
                self.set_status("یک کلید غیر از Ctrl/Shift/Alt را هم فشار دهید.")
                return True

            self.hotkey_input.setText(hotkey)
            self.stop_hotkey_recording(cancelled=False)
            return True
        return super().eventFilter(watched, event)

    def _create_tray(self) -> QSystemTrayIcon | None:
        if not QSystemTrayIcon.isSystemTrayAvailable():
            return None
        tray = QSystemTrayIcon(self)
        tray.setIcon(QIcon(str(ICON_DIR / "icons8-keyboard-96.ico")))
        menu = QMenu()
        show_action = QAction("نمایش", self)
        show_action.triggered.connect(self._show_from_tray)
        quit_action = QAction("خروج", self)
        quit_action.triggered.connect(self.quit_app)
        menu.addAction(show_action)
        menu.addAction(quit_action)
        tray.setContextMenu(menu)
        tray.activated.connect(self._tray_activated)
        tray.show()
        return tray

    def _tray_activated(self, reason) -> None:
        if reason == QSystemTrayIcon.ActivationReason.DoubleClick:
            self._show_from_tray()

    def _show_from_tray(self) -> None:
        self.showNormal()
        self.activateWindow()
        self.raise_()

    def closeEvent(self, event) -> None:
        if self.tray is not None and self.tray.isVisible():
            event.ignore()
            self.hide()
            self.tray.showMessage("Keyboard Layout Mapper", "برنامه در System Tray فعال ماند.")
            return
        super().closeEvent(event)

    def quit_app(self) -> None:
        from PyQt6.QtWidgets import QApplication
        QApplication.quit()

    def save_settings(self) -> None:
        self.config = {
            "hotkey": self.hotkey_input.text().strip() or DEFAULT_HOTKEY,
            "mode": self.mode_input.currentData(),
            "restore_clipboard": self.restore_clipboard.isChecked(),
            "autostart": self.autostart_checkbox.isChecked(),
        }
        save_config(self.config)
        set_autostart(self.config["autostart"])
        self.hotkey_service.start(self.config["hotkey"])

    def start_hotkey_recording(self) -> None:
        self.is_recording_hotkey = True
        self.hotkey_service.stop()
        self.record_button.setText("در حال ضبط... (Esc برای لغو)")
        self.set_status("کلیدهای شورتکات جدید را فشار دهید.")

    def stop_hotkey_recording(self, cancelled: bool) -> None:
        self.is_recording_hotkey = False
        self.record_button.setText("ضبط شورتکات")
        if cancelled:
            self.set_status("ضبط شورتکات لغو شد.")
            self.hotkey_service.start(self.config["hotkey"])
            return
        self.save_settings()

    def set_status(self, message: str) -> None:
        self.status_label.setText(message)
        if self.tray is not None:
            self.tray.setToolTip(message)

    def update_preview(self) -> None:
        self.preview_output.setPlainText(map_text(self.preview_input.toPlainText()))

    def transform_focused_text(self) -> None:
        QTimer.singleShot(180, lambda: _transform_focused_text(self.config, self.set_status))


def _transform_focused_text(config: dict, set_status) -> None:
    from PyQt6.QtGui import QGuiApplication
    from .input_sender import send_shortcut

    clipboard = QGuiApplication.clipboard()
    old_clipboard_text = clipboard.text()
    if config["mode"] == "field":
        send_shortcut("ctrl+a")
        import time
        time.sleep(0.08)
    send_shortcut("ctrl+c")
    QTimer.singleShot(180, lambda: _replace_target_text(config, set_status, old_clipboard_text))


def _replace_target_text(config: dict, set_status, old_clipboard_text: str) -> None:
    from PyQt6.QtGui import QGuiApplication
    from .input_sender import send_shortcut

    clipboard = QGuiApplication.clipboard()
    text = clipboard.text()
    if not text:
        set_status("متنی برای تبدیل پیدا نشد؛ ابتدا متن را انتخاب کنید.")
        return
    converted_text = map_text(text)
    clipboard.setText(converted_text)
    send_shortcut("ctrl+v")
    set_status("متن تبدیل شد.")
    if config["restore_clipboard"]:
        QTimer.singleShot(700, lambda: clipboard.setText(old_clipboard_text))

# Keyboard Layout Mapper

[![Python](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Platform](https://img.shields.io/badge/platform-Linux-lightgrey.svg)](https://github.com/mtgama/lang_change)

A fast keyboard layout converter for Persian and English with global hotkey support.

## Features

- Convert text between Persian and English keyboard layouts
- Global hotkey support (X11/pynput)
- System tray integration
- Autostart on system login
- Simple and clean UI

## Installation

### From source

```bash
git clone https://github.com/mtgama/lang_change.git
cd lang_change
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### Running

```bash
python run.py
```

### Building binary

```bash
pip install pyinstaller
pyinstaller --onefile --noconsole --name changekeyboard run.py
```

The binary will be in `dist/changekeyboard`.

## Usage

1. Launch the application
2. Set your preferred hotkey (default: `Ctrl+Shift+L`)
3. Select the conversion mode:
   - **Selection mode**: Select text and press hotkey
   - **Field mode**: Click in a text field and press hotkey (selects all with Ctrl+A)
4. Click "ذخیره و فعال‌سازی شورتکات" to save

### Command line options

```bash
changekeyboard                  # Normal mode
changekeyboard --minimized      # Start minimized to tray
changekeyboard --convert-focused # Convert focused text and exit
```

### Autostart

Enable "شروع خودکار هنگام ورود به سیستم" in settings to start the app on system login.

## Project Structure

```
lang_change/
├── src/
│   └── keyboard_layout_mapper/
│       ├── __init__.py      # Package metadata
│       ├── __main__.py      # Module execution
│       ├── main.py          # Entry point
│       ├── config.py        # Configuration management
│       ├── mapper.py        # Text mapping logic
│       ├── hotkey.py        # Global hotkey service
│       ├── input_handler.py # Qt key event handling
│       ├── input_sender.py  # Keyboard shortcut injection
│       └── ui.py            # Main window UI
├── assets/
│   ├── icons8-keyboard-96.png
│   └── icons8-keyboard-96.ico
├── tests/
├── run.py                   # Development entry point
├── requirements.txt
├── pyproject.toml
├── LICENSE
└── README.md
```

## Requirements

- Python 3.8+
- PyQt6
- pynput
- python-xlib

## License

MIT License - see [LICENSE](LICENSE) for details.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## Author

**mtgama** - [GitHub](https://github.com/mtgama)

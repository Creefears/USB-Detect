# USB Detect

**🌐 Language: [Français](README.md) | English**

> [!CAUTION]
> ## IMPORTANT — DISCLAIMER
> This software was **designed entirely with the help of artificial intelligence**.
> It is provided **as-is**, with no guarantee of flawless operation, security, or fitness for production use.
> Use it at your own risk and test it carefully before any deployment.

---

## Why this project?

This project was born out of a personal need: **no satisfactory alternative existed** to automate actions based on the connection/disconnection of USB devices on Windows.

For a long time, I relied on a small, hand-made **AutoHotkey script** that did the job — but in a shaky and potentially dangerous way for my system. No interface, no proper process management, no updates.

Having found no software that met this need, I decided to build **USB Detect** with the help of an AI. The result is a clean, reliable, and configurable tool that replaces that homemade solution.

---

## Overview
**USB Detect** is a lightweight tool that monitors, in real time, the connection and disconnection of USB devices on Windows.

The program can:
* **Detect** USB, HID, and monitor devices automatically.
* **Log** events (connection / disconnection).
* **Trigger** custom actions (launch/close applications, commands).
* **Enable/Disable** each macro individually without deleting it.
* **Start with Windows** and run in the background in the system tray.
* **Check for updates** automatically on GitHub.
* **Self-install** into Program Files on first launch.
* **Choose the interface language** (French or English).

It is designed to run in the background with minimal resource usage.

---

## Key features
* **Real-time USB monitoring** via WMI.
* **Full event logging.**
* **Configurable automatic actions** (launch, close, commands).
* **Execution conditions** (number of monitors, presence of other devices).
* **Per-macro enable/disable.**
* **Automatic startup** with Windows (option in the settings).
* **System tray mode** — minimizes to the taskbar.
* **Automatic updates** — notification and direct link to GitHub.
* **Configuration preserved** across updates.
* **Bilingual interface** (French / English).

---

## Project structure
* **main.py**: PyQt6 graphical interface
* **engine.py**: Detection and action engine
* **wizard.py**: Device add/edit wizard
* **i18n.py**: Translation system (French / English)
* **build.py**: Build script to generate the executable
* **config.example.json**: Default configuration (template)
* **config.json**: User configuration (created on first launch)
* **usb_detect.ico**: Application icon

---

## Requirements
* Windows 10/11
* Python 3.10+
* Python dependencies: `pip install -r requirements.txt`

---

## Installation

### Download the executable (recommended)
1. Download the `.exe` from the [Releases page](https://github.com/Creefears/USB-Detect/releases)
2. Double-click the file — the installer launches automatically
3. The application installs into `C:\Program Files\USB Detect\`
4. A shortcut is created in the Start menu

User data (configuration, logs) is stored in `%APPDATA%\USB Detect\`.

### From source (developers)
1. **Clone the repository:**
   ```
   git clone https://github.com/Creefears/USB-Detect.git
   ```
2. **Enter the folder:**
   ```
   cd USB-Detect
   ```
3. **Install the dependencies:**
   ```
   pip install -r requirements.txt
   ```
4. **Run the program:**
   ```
   pythonw main.py
   ```

### Build the executable (.exe)
```
pip install pyinstaller Pillow
python build.py
```
The executable will be in the `dist/` folder.

---

## Configuration

Configuration is done through the graphical interface or the `config.json` file.

On first launch, `config.json` is created automatically from `config.example.json` in `%APPDATA%\USB Detect\`.

**Important:** `config.json` is ignored by Git and preserved across updates.

### Available settings
| Setting | Description |
|---|---|
| `language` | Interface language: `fr`, `en`, or `""` (auto-detection) |
| `start_with_windows` | Launch at Windows startup |
| `start_in_tray` | Start in the background (system tray) |
| `start_minimized` | Start with the window minimized |
| `notifications_enabled` | Enable notifications |
| `log_enabled` | Enable logs |

### Changing the language
The language is selected under **Settings → Language**. On first launch, the language is detected automatically from the system locale (English by default outside a French-speaking environment). A language change takes effect after the application is restarted.

### PowerShell commands
For a "command" type action, USB Detect automatically detects PowerShell commands (those starting with `powershell`/`pwsh`, ending with `.ps1`, or using PowerShell syntax such as `$env:` or cmdlets) and runs them through PowerShell instead of `cmd.exe`. This means a command like:
```
powershell -ExecutionPolicy Bypass -File "$env:USERPROFILE\Documents\script.ps1"
```
works as expected, with PowerShell variables correctly expanded.

---

## How it works
The software polls the system every 5 seconds. When a USB device is:
* **Connected:** the connection actions are executed.
* **Disconnected:** the disconnection actions are executed.

Each macro can be **enabled or disabled** individually using the ON/OFF button.

---

## Updates
USB Detect automatically checks for updates on GitHub at startup. If a new version is available, a banner appears with a button to reach the download page.

When an update is applied, a **"What's new"** window is shown automatically to present the version's changes.

The update preserves your configuration (macros, settings).

---

## Known limitations
* Designed primarily for Windows.
* Relies on USB device detection via WMI.
* Not tested in critical environments.

---

## Security notice
This project is provided for educational purposes. Before any production use, test it in a controlled environment and validate the automatic actions.

---

## Credits
This software was designed entirely with the help of artificial intelligence, then tested and integrated by the user.

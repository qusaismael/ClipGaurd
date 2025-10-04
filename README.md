# 🛡️ ClipGuard

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](https://opensource.org/licenses/MIT)
[![Python 3.7+](https://img.shields.io/badge/python-3.7+-blue.svg)](https://www.python.org/downloads/)
[![Platform: Linux](https://img.shields.io/badge/platform-Linux-green.svg)](https://www.linux.org/)

**ClipGuard** is a lightweight, privacy-focused system tray application for Linux that automatically masks sensitive information in your clipboard. Protect your privacy when copying and pasting emails, phone numbers, credit cards, IP addresses, and more.

<p align="center">
  <img src="https://img.shields.io/badge/status-stable-brightgreen" alt="Status">
  <img src="https://img.shields.io/badge/UI-PyQt6-blue" alt="UI">
  <img src="https://img.shields.io/badge/works%20on-X11%20%7C%20Wayland-orange" alt="Display Server">
</p>

---

## ✨ Features

### 🔒 **Automatic Sensitive Data Masking**
- **Email addresses** → `[REDACTED_EMAIL]`
- **Phone numbers (US format)** → `[REDACTED_PHONE]`
- **IPv4 addresses** → `[REDACTED_IP]`
- **Credit card numbers** → `[REDACTED_CC]`
- **Social Security Numbers** → `[REDACTED_SSN]`

### 🧠 **Smart Detection**
ClipGuard only masks sensitive data when it's part of larger text. If you copy just an email address alone, it won't be masked—we assume you copied it intentionally.

### 🔗 **Link Cleaning**
Remove tracking parameters and unwrap redirectors:
- Strips `utm_*`, `fbclid`, `gclid`, `mc_eid`, `igshid`
- Unwraps Google and Facebook redirectors
- Converts AMP URLs to canonical form

### ⚙️ **Fully Customizable**
- Enable/disable any built-in rule
- Add custom regex patterns for your specific needs
- Settings saved to `~/.config/clipguard/settings.json`

### 🔄 **Restore Original Content**
Made a mistake? Use "Restore Last Content" to get back the unmasked text anytime.

### 🎨 **Beautiful Modern UI**
- Clean, professional interface with emoji icons
- Tabbed settings dialog with built-in help
- Smart notifications with content previews
- Tooltips on every element

---

## 🚀 Installation

### Prerequisites

All distributions require:
- **Python 3.7+**
- **xclip** or **xsel** (for clipboard access)

---

### 📦 Debian / Ubuntu / Linux Mint / Pop!_OS

```bash
# Install system dependencies
sudo apt update
sudo apt install python3 python3-pip python3-venv xclip git

# Clone the repository
git clone https://github.com/qusaismael/ClipGuard.git
cd ClipGuard

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install Python dependencies
pip install -r requirements.txt

# Run ClipGuard
./run.sh
```

**Optional: Add to autostart**
```bash
mkdir -p ~/.config/autostart
cp clipguard.desktop ~/.config/autostart/
```

---

### 📦 Fedora / RHEL / CentOS

```bash
# Install system dependencies
sudo dnf install python3 python3-pip xclip git

# Clone the repository
git clone https://github.com/qusaismael/ClipGuard.git
cd ClipGuard

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install Python dependencies
pip install -r requirements.txt

# Run ClipGuard
./run.sh
```

**Auto-start on Login (Fedora/RHEL):**
```bash
mkdir -p ~/.config/autostart
cp clipguard.desktop ~/.config/autostart/
```

---

### 📦 Arch Linux / Manjaro

```bash
# Install system dependencies
sudo pacman -S python python-pip xclip git

# Clone the repository
git clone https://github.com/qusaismael/ClipGuard.git
cd ClipGuard

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install Python dependencies
pip install -r requirements.txt

# Run ClipGuard
./run.sh
```

**Auto-start on Login (Arch/Manjaro):**
```bash
mkdir -p ~/.config/autostart
cp clipguard.desktop ~/.config/autostart/
```

**AUR Package (Coming Soon)**
```bash
yay -S clipguard
```

---

### 📦 openSUSE

```bash
# Install system dependencies
sudo zypper install python3 python3-pip xclip git

# Clone the repository
git clone https://github.com/qusaismael/ClipGuard.git
cd ClipGuard

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install Python dependencies
pip install -r requirements.txt

# Run ClipGuard
./run.sh
```

**Auto-start on Login (openSUSE):**
```bash
mkdir -p ~/.config/autostart
cp clipguard.desktop ~/.config/autostart/
```

---

### 📦 Universal Install (Any Distribution)

If your distribution isn't listed above:

```bash
# Ensure you have Python 3.7+ and pip installed
python3 --version
pip3 --version

# Install xclip or xsel (check your package manager)
# Examples:
# sudo apt install xclip       # Debian-based
# sudo dnf install xclip       # Fedora-based
# sudo pacman -S xclip         # Arch-based
# sudo zypper install xclip    # openSUSE

# Clone and set up
git clone https://github.com/qusaismael/ClipGuard.git
cd ClipGuard
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
./run.sh
```

---

## 📖 Quick Start

### 1. **Launch ClipGuard**
```bash
./run.sh
```
or
```bash
python3 main.py
```

### 2. **Verify It's Running**
Look for a green shield icon (🛡️) in your system tray.

### 3. **Test Masking**
Copy this text:
```
Contact me at john.doe@example.com or call 555-123-4567
```

Paste it somewhere and you should see:
```
Contact me at [REDACTED_EMAIL] or call [REDACTED_PHONE]
```

### 4. **Test Restore**
Right-click the tray icon → **"🔄 Restore Last Content"** → Paste again to see the original.

### 5. **Explore Settings**
Right-click the icon → **"⚙️ Settings"**
- Browse built-in rules
- Add custom patterns
- Read the Help tab for examples

---

## 🎯 Usage

### System Tray Menu

Right-click the ClipGuard icon to access:

```
📊 Status
  ⏸️  Stop Monitoring       Toggle protection on/off

⚡ Quick Actions
  🔄  Restore Last Content  Get back unmasked text
  🔗  Clean Last Link       Remove URL tracking

  ⚙️  Settings              Customize masking rules
  ℹ️  About ClipGuard       Learn about features

  ❌  Quit                  Exit application
```

### Adding Custom Rules

1. Open **Settings** from the tray menu
2. Go to the **"🔒 Masking Rules"** tab
3. Fill in the **"Add Custom Rule"** section:
   - **Name**: Descriptive name (e.g., "API Key")
   - **Pattern**: Regex pattern (e.g., `sk-[A-Za-z0-9]{48}`)
   - **Replacement**: Placeholder (e.g., `[REDACTED_API_KEY]`)
4. Click **"➕ Add Rule"**
5. Click **"💾 Save & Close"**

**Examples:**

| Name | Pattern | Replacement |
|------|---------|-------------|
| OpenAI API Key | `sk-[A-Za-z0-9]{48}` | `[REDACTED_API_KEY]` |
| Bitcoin Address | `\b[13][a-km-zA-HJ-NP-Z1-9]{25,34}\b` | `[REDACTED_BTC]` |
| Employee ID | `EMP-\d{6}` | `[REDACTED_EMP_ID]` |
| AWS Key | `AKIA[0-9A-Z]{16}` | `[REDACTED_AWS_KEY]` |

---

## 🖥️ Desktop Integration

### Add to Application Menu (All Distributions)

```bash
mkdir -p ~/.local/share/applications
cp clipguard.desktop ~/.local/share/applications/
chmod +x ~/.local/share/applications/clipguard.desktop
update-desktop-database ~/.local/share/applications
```

ClipGuard will now appear in your application menu under "Utilities" or "Security".

### Auto-Start on Login (All Distributions)

Make ClipGuard start automatically when you log in:

```bash
mkdir -p ~/.config/autostart
cp clipguard.desktop ~/.config/autostart/
```

This works on **all distributions**:
- ✅ Ubuntu / Debian / Linux Mint / Pop!_OS
- ✅ Fedora / RHEL / CentOS
- ✅ Arch Linux / Manjaro
- ✅ openSUSE
- ✅ Any distribution with XDG autostart support

**Verify it's enabled:**
```bash
ls -la ~/.config/autostart/clipguard.desktop
```

**To disable autostart:**
```bash
rm ~/.config/autostart/clipguard.desktop
```

### System Tray Icon Not Showing?

**GNOME Users:** Install the "AppIndicator and KStatusNotifierItem Support" extension.

```bash
# Ubuntu/Debian
sudo apt install gnome-shell-extension-appindicator

# Fedora
sudo dnf install gnome-shell-extension-appindicator

# Arch
sudo pacman -S gnome-shell-extension-appindicator-git
```

Then enable it in GNOME Extensions/Tweaks.

---

## 📋 Configuration

Settings are stored in: `~/.config/clipguard/settings.json`

**Example configuration:**
```json
{
  "monitoring_active": true,
  "builtin_patterns": {
    "Email": {
      "pattern": "\\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\\.[A-Z|a-z]{2,}\\b",
      "replacement": "[REDACTED_EMAIL]",
      "enabled": true
    }
  },
  "custom_patterns": {
    "API Key": {
      "pattern": "sk-[A-Za-z0-9]{48}",
      "replacement": "[REDACTED_API_KEY]",
      "enabled": true,
      "custom": true
    }
  }
}
```

---

## 🧪 Testing

Run the included test scripts to verify functionality:

### Test Cross-Application Monitoring
```bash
./test_cross_app.py
```

### Test Restore Feature
```bash
./test_restore.py
```

For comprehensive testing instructions, see **[TESTING.md](TESTING.md)**.

---

## 🛠️ Troubleshooting

### Clipboard Not Being Monitored

1. **Check monitoring is enabled**: Icon should be green
2. **Install xclip or xsel**: `sudo apt install xclip`
3. **Check console for errors**: `python3 main.py`

### System Tray Icon Not Showing

1. Install system tray extension (see Desktop Integration above)
2. Check if your DE supports system tray
3. Try restarting your desktop environment

### Permission Errors

```bash
chmod +x run.sh main.py test_*.py
```

### Python Dependencies Issues

```bash
# Update pip
pip install --upgrade pip

# Reinstall dependencies
pip install -r requirements.txt --force-reinstall
```

---

## 📚 Documentation

- **[INSTALL.md](INSTALL.md)** - Detailed installation guide
- **[TESTING.md](TESTING.md)** - Testing procedures
- **[UI_GUIDE.md](UI_GUIDE.md)** - Complete UI tour
- **[WHATS_NEW.md](WHATS_NEW.md)** - v1.1 feature announcement
- **[CHANGELOG.md](CHANGELOG.md)** - Version history

---

## 🤝 Contributing

Contributions are welcome! Here's how you can help:

1. **Fork the repository**
2. **Create a feature branch**: `git checkout -b feature/amazing-feature`
3. **Commit your changes**: `git commit -m 'Add amazing feature'`
4. **Push to the branch**: `git push origin feature/amazing-feature`
5. **Open a Pull Request**

### Development Setup

```bash
# Clone your fork
git clone https://github.com/qusaismael/ClipGuard.git
cd ClipGuard

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run in development mode
python3 main.py
```

### Code Style

- Follow PEP 8
- Add docstrings to functions and classes
- Comment complex logic
- Test your changes thoroughly

---

## 📝 License

This project is licensed under the **MIT License** - see the [LICENSE](LICENSE) file for details.

---

## 🙏 Acknowledgments

Built with:
- **[PyQt6](https://www.riverbankcomputing.com/software/pyqt/)** - Modern GUI framework
- **[pyperclip](https://github.com/asweigart/pyperclip)** - Cross-platform clipboard access
- **Python 3** - Powerful and elegant

Inspired by the need for privacy-conscious computing on Linux.

---

## 🌟 Stars

If you find ClipGuard useful, please consider giving it a star! ⭐

---

## 🔐 Security

ClipGuard processes all data **locally** on your machine. No data is ever sent over the network.

If you discover a security vulnerability, You can open an issue above.

---

## 🗺️ Roadmap

- [ ] Support for more data types (passport numbers, dates of birth, etc.)
- [ ] Multi-language phone number support
- [ ] Clipboard history with auto-masking
- [ ] Export/import custom rules
- [ ] Dark mode theme
- [ ] Flatpak/Snap package
- [ ] Wayland-native implementation

---

## 💝 Support This Project

If ClipGuard helps protect your privacy, consider:
- ⭐ **Starring** this repository
- 🐛 **Reporting bugs** you encounter
- 💡 **Suggesting features** you'd like to see
- 📖 **Contributing** code or documentation
- 🗣️ **Spreading the word** to friends and colleagues

---

<p align="center">
  Made with ❤️ for privacy-conscious Linux users
</p>

<p align="center">
  <b>ClipGuard v1.0</b> | October 2025
</p>

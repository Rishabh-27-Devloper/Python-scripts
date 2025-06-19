# InstaFocusMode 🔊

A desktop application that helps you stay focused by detecting when Instagram is open and displaying an interactive, game-like fullscreen overlay to remind you to close it and return to work or study. Built with Python and Tkinter.

---

## 🚀 Features

* ✅ Cross-platform support (Windows, macOS, Linux)
* ⏳ Real-time monitoring of running processes and active windows
* 🤖 Game-style overlay with animated character when Instagram is detected
* ⌛ Auto-dismiss overlay after 1 minute or on click
* ⚖ Lightweight and runs in background thread

---

## 💾 Installation

Make sure Python 3.6+ is installed.

Install required dependencies (auto-installed if missing):

```bash
pip install pywin32 psutil pillow requests
```

Then run the script:

```bash
python InstaFocusMode.py
```

---

## 🌐 Supported Platforms

* Windows 10+
* macOS (using AppleScript)
* Linux (requires `xdotool`)

---

## 🔧 How It Works

1. **Monitors** for Instagram processes or window titles.
2. If detected, it **triggers a fullscreen overlay** with a motivational message.
3. Overlay has a cute animated robot and message: “FOCUS TIME! Close Instagram and get back to Study!”
4. Click anywhere or wait 60 seconds to dismiss.

---

## 📁 Project Structure

```
InstaFocusMode.py   # Main script
```

---

## 🏆 Highlights

* 🌍 Uses platform-specific methods to detect Instagram reliably
* 🚀 Fast and responsive UI using `Tkinter`
* ✨ Motivational overlay character to encourage productivity

---

## ✍️ Author

Developed by [Rishabh-27-Devloper](https://github.com/Rishabh-27-Devloper)

---

## ⚖️ License

[GNU General Public License v3.0](https://www.gnu.org/licenses/gpl-3.0.en.html)

---

## 📈 Contributions

PRs and issues are welcome! Help enhance detection accuracy, add new platforms, or improve the UI.

---

## 📊 Screenshots

> *Coming soon: Add screenshots of the overlay in action!*

---

## 🚨 Disclaimer

This tool is a productivity assistant. Use responsibly and customize if needed to suit your workflow.

---

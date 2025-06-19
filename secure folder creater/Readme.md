# Secure Folder Manager Gen 2

![Python](https://img.shields.io/badge/Python-3.10-blue)
![Tkinter](https://img.shields.io/badge/Tkinter-GUI-lightgrey)
![License: GPLv3](https://img.shields.io/badge/License-GPLv3-blue)

Secure Folder Manager Gen 2 is an enhanced version of the original Secure Folder tool designed to offer a safer and more persistent way to store sensitive files. It ensures data is stored in OS-specific application directories (e.g., AppData or \~/.local/share) rather than temporary folders, and it offers migration from Gen 1, improved cross-platform support, and enhanced security through password protection.

---

## Features

* ✅ Secure file storage in non-volatile, hidden directories
* ✅ Password-protected access with SHA-256 hashing
* ✅ GUI built using Tkinter (cross-platform)
* ✅ Automatic migration from Gen 1 (temporary folders)
* ✅ File management (add, delete, open) with explorer-like view
* ✅ No folder-level navigation (security-first design)
* ✅ Detailed storage info and password management

---

## Installation

### Requirements:

* Python 3.6+
* tkinter (usually included)
* `pywin32` (Windows only):

```bash
pip install pywin32
```

---

## Usage

```bash
python Secure\ Folder\ Gen2.py
```

On first launch, you will be prompted to:

* Set a master password (hashed and stored securely)
* Allow migration from older Gen 1 secure folder (if detected)

---

## File Locations (Per OS)

| OS      | Storage Location                                    |
| ------- | --------------------------------------------------- |
| Windows | `%LOCALAPPDATA%/SecureFolderManager`                |
| macOS   | `~/Library/Application Support/SecureFolderManager` |
| Linux   | `~/.local/share/SecureFolderManager`                |

---

## Screenshots

> (Add screenshots of the UI, migration prompt, file explorer view, etc. here)

---

## Security Measures

* Files are not stored in temporary folders
* Passwords are hashed using SHA-256
* System-specific hidden folders
* Migration from Gen 1 handled securely with backup option

---

## Limitations

* Folder-level navigation is restricted (read-only view)
* Only individual files can be added (no drag & drop support in Gen 2)

---

## License

This project is licensed under the [GNU GPLv3 License](https://www.gnu.org/licenses/gpl-3.0.html).

---

## Author

**Prakhar Shukla**
Email: [Rishabh27@outlook.in](mailto:Rishabh27@outlook.in)
GitHub: [Rishabh-27-Devloper](https://github.com/Rishabh-27-Devloper)

---

## Contributing

Pull requests and issues are welcome. Feel free to fork this repository and submit enhancements or bug fixes!

---

## Disclaimer

This tool is intended for local personal use. It does not use encryption beyond password-based access control. For advanced security, consider file-level encryption or professional-grade vaults.

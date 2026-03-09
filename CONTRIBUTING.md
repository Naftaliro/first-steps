# Contributing to First Steps

Thank you for your interest in contributing to First Steps! This document provides guidelines and information for contributors.

## Code of Conduct

Please be respectful and constructive in all interactions. We are committed to providing a welcoming and inclusive experience for everyone.

## How to Contribute

### Reporting Bugs

1. Check the [existing issues](https://github.com/Naftaliro/first-steps/issues) to avoid duplicates.
2. Open a new issue with a clear title and description.
3. Include your OS version, desktop environment, and steps to reproduce.

### Suggesting Features

Open an issue with the "enhancement" label describing:
- What problem the feature solves
- How you envision it working
- Any alternatives you considered

### Submitting Code

1. Fork the repository and create a feature branch from `main`.
2. Follow the existing code style (PEP 8, type hints, docstrings).
3. Ensure every new file includes the SPDX license header:
   ```python
   # SPDX-License-Identifier: GPL-3.0-or-later
   # Copyright 2026 First Steps Contributors
   ```
4. Test your changes on a Zorin OS 18 / Ubuntu 24.04 system.
5. Submit a pull request with a clear description of changes.

## Development Setup

### Prerequisites

- Python 3.10+
- GTK 4 and LibAdwaita development libraries
- Flatpak (for Flatpak-related features)

### Install Dependencies

```bash
sudo apt install python3-gi gir1.2-gtk-4.0 gir1.2-adw-1 flatpak
```

### Run from Source

```bash
git clone https://github.com/Naftaliro/first-steps.git
cd first-steps
./first-steps
```

### Project Structure

```
first-steps/
├── first_steps/           # Python package
│   ├── __init__.py        # Version and app ID
│   ├── app.py             # Main application and window
│   ├── updater.py         # Auto-update checker
│   ├── pages/             # Wizard pages (one file per page)
│   │   ├── __init__.py    # BasePage class
│   │   ├── welcome.py
│   │   ├── codecs.py
│   │   ├── flatpak.py
│   │   ├── drivers.py
│   │   ├── bottles.py
│   │   ├── timeshift.py
│   │   ├── power.py
│   │   ├── firewall.py
│   │   ├── extras.py
│   │   └── summary.py
│   └── helpers/           # Helper modules
├── scripts/               # Helper and installer scripts
├── data/                  # Desktop entry, icons, polkit policy
├── packaging/             # .deb packaging files
└── install.sh             # Source install script
```

### Building the .deb Package

```bash
./packaging/build-deb.sh
```

The output `.deb` will be in `packaging/deb/`.

## Coding Guidelines

- Use **GTK4 + LibAdwaita** patterns for all UI elements.
- Run system commands via `BasePage.run_privileged()` or `BasePage.run_unprivileged()` to keep the UI responsive.
- Never run blocking operations on the main thread.
- Use `pkexec` for privileged operations; never ask for passwords directly.
- All privileged scripts must be placed in `/tmp/first-steps-*` for the helper validation.

## License

By contributing, you agree that your contributions will be licensed under the GPL-3.0-or-later license.

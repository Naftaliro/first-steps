# First Steps — Onboarding Wizard for Zorin OS

A GTK4 + LibAdwaita onboarding wizard for Zorin OS 18 and other Ubuntu-based systems. Think of it like a welcome wizard that actually *does things*, not just shows links. Clean, checkbox-driven interface for everything you need on a fresh install.

---

## Installation

### One-Liner Install (Recommended)

Paste this into a terminal and you're done:

```bash
curl -fsSL https://raw.githubusercontent.com/Naftaliro/first-steps/main/scripts/install-online.sh | sudo bash
```

This automatically installs all dependencies, downloads the latest release, **verifies its SHA-256 checksum**, and sets everything up. To uninstall: `sudo apt remove first-steps`.

### Download the .deb Package

Grab the `.deb` from the [Releases page](https://github.com/Naftaliro/first-steps/releases/latest) and double-click it, or install the latest version from the terminal:

```bash
# Automatically download the latest .deb from GitHub Releases
DEB_URL=$(curl -fsSL https://api.github.com/repos/Naftaliro/first-steps/releases/latest \
  | grep -o '"browser_download_url"[^"]*\.deb"' | grep -o 'https://[^"]*')
wget "$DEB_URL" -O first-steps-latest.deb
sudo apt install ./first-steps-latest.deb
```

### Install from Source

```bash
git clone https://github.com/Naftaliro/first-steps.git
cd first-steps
sudo ./install.sh
```

To uninstall: `sudo ./install.sh remove`

---

## Features

### Setup Pages (14 total)

| Page | What It Does |
|------|-------------|
| **Welcome** | System info card (OS, CPU, GPU, RAM, disk), overview of all sections |
| **Codecs & Media** | One-click install of `ubuntu-restricted-extras`, GStreamer plugins (good/bad/ugly/libav), DVD support, VA-API |
| **Flatpak & Apps** | Detects/enables Flathub, curated picker of 16 apps across Media, Productivity, Internet, Gaming, Development |
| **Drivers** | Wraps `ubuntu-drivers devices` — scans hardware, shows recommended flags, one-click install |
| **Windows Apps** | Installs Bottles via Flatpak, optional Wine deps + GameMode, guided first-bottle creation |
| **Backup** | Installs + configures Timeshift — schedule toggles, retention spinners, home exclusion, first snapshot |
| **Power** | Power profile dropdown, lid behavior for AC/battery, auto-suspend timeouts, screen dim toggle |
| **Firewall** | Enables UFW with deny-incoming/allow-outgoing defaults, 8 common service exceptions |
| **Network** | Connectivity check (HTTP/DNS/latency), DNS configuration (Cloudflare/Google/Quad9), network tools installer |
| **Privacy** | Disable Ubuntu telemetry/Whoopsie/popularity-contest, GNOME privacy settings, browser extension recommendations |
| **Development** | Git identity config, code editor installer (VS Code/Codium/Zed/etc.), Docker/Podman, language runtimes, dev utilities |
| **Language** | Language packs (12 languages), input methods (IBus/Fcitx5), spell-check dictionaries, font installer (Noto/Fira/Cascadia) |
| **Extras** | Theme Switcher installer, theme packs, system update, accessibility toggles, utility installer |
| **Summary** | Live recap of all actions + export setup report as Markdown + recommended next steps |

### UX Features

| Feature | Details |
|---------|---------|
| **Dark/Light Mode Toggle** | One-click toggle in the header bar (Ctrl+D) |
| **Sidebar Progress Indicators** | Green checkmarks appear next to completed sections |
| **Skip / "I've Done This"** | Every page has a skip button for power users who've already configured things |
| **Keyboard Shortcuts** | Ctrl+1–0 for page navigation, Ctrl+Q to quit, Ctrl+D for dark mode |
| **Export Setup Report** | Save a Markdown report of everything configured during the session |
| **Auto-Update** | Checks GitHub Releases on launch, offers one-click in-app upgrade |
| **Toast Notifications** | Every action shows success/failure feedback via in-app toasts |
| **Privileged Operations** | Uses `pkexec` with a dedicated polkit policy — one auth prompt, no terminal |
| **Async Execution** | All installs run in background threads with spinner feedback |

---

## Legal & Licensing

This project is licensed under the **GNU General Public License v3.0 or later**.

- A copy of the license is available in the [LICENSE](LICENSE) file.
- The application icon is original work created for this project and is also licensed under GPL-3.0-or-later.
- This project is not affiliated with or endorsed by Zorin Group. All branding is original to "First Steps" to avoid trademark infringement.
- For a full list of dependencies and their licenses, see the [NOTICE](NOTICE) file.
- A comprehensive licensing audit is available in [LICENSING-AUDIT.md](LICENSING-AUDIT.md).

## Security

The one-liner installer verifies SHA-256 checksums before installing. To report a security vulnerability, please see [SECURITY.md](SECURITY.md) for responsible disclosure instructions.

## Contributing

Contributions are welcome! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines on reporting bugs, suggesting features, and submitting code.

## Development

The application is written in Python using the PyGObject bindings for GTK4 and Libadwaita.

| Component | Path |
|-----------|------|
| Main Application | `first_steps/app.py` |
| Auto-Update Module | `first_steps/updater.py` |
| UI Pages (14) | `first_steps/pages/` |
| Base Page Class | `first_steps/pages/__init__.py` |
| Privileged Helper | `scripts/first-steps-helper` |
| Polkit Policy | `data/io.github.firststeps.policy` |
| Install Script | `install.sh` |
| .deb Build Script | `packaging/build-deb.sh` |
| Online Installer | `scripts/install-online.sh` |
| Tests (50+) | `tests/` |

To run from the source tree without installing:

```bash
./first-steps
```

To rebuild the .deb package:

```bash
./packaging/build-deb.sh
```

To run the test suite:

```bash
python3 -m pytest tests/ -v
```

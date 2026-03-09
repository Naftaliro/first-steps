# First Steps — Onboarding Wizard for Zorin OS

A GTK4 + LibAdwaita onboarding wizard for Zorin OS 18 and other Ubuntu-based systems. Think of it like a welcome wizard that actually *does things*, not just shows links. Clean, checkbox-driven interface for everything you need on a fresh install.

---

## Installation

### One-Liner Install (Recommended)

Paste this into a terminal and you're done:

```bash
curl -fsSL https://raw.githubusercontent.com/Naftaliro/first-steps/main/scripts/install-online.sh | sudo bash
```

This automatically installs all dependencies, downloads the latest release, and sets everything up. To uninstall: `sudo apt remove first-steps`.

### Download the .deb Package

Grab the `.deb` from the [Releases page](https://github.com/Naftaliro/first-steps/releases/latest) and double-click it, or install from the terminal:

```bash
wget https://github.com/Naftaliro/first-steps/releases/latest/download/first-steps_1.1.0-1_all.deb
sudo apt install ./first-steps_1.1.0-1_all.deb
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

| Page | What It Does |
|------|-------------|
| **Welcome** | Overview of all setup sections with a quick-start guide |
| **Codecs & Media** | One-click install of `ubuntu-restricted-extras`, GStreamer plugins (good/bad/ugly/libav), DVD support, and VA-API hardware acceleration |
| **Flatpak & Apps** | Detects/enables Flathub, then offers a curated picker of 16 apps across Media, Productivity, Internet, Gaming, and Development |
| **Drivers** | Wraps `ubuntu-drivers devices` — scans hardware, shows results with recommended flags, one-click install |
| **Windows Apps** | Installs Bottles via Flatpak, optional Wine deps + GameMode, guided first-bottle creation with template picker |
| **Backup** | Installs + configures Timeshift — schedule toggles (weekly/daily/boot), retention spinners, home exclusion, "Create First Snapshot" button |
| **Power** | Power profile dropdown (power-saver/balanced/performance), lid behavior for AC and battery, auto-suspend timeouts, screen dim toggle |
| **Firewall** | Enables UFW with deny-incoming/allow-outgoing defaults, 8 common service exceptions (SSH, KDE Connect, CUPS, etc.) |
| **Extras** | Theme Switcher installer, theme packs, system update, accessibility toggles (large text, high contrast, large cursor, reduce animations), utility installer |
| **Summary** | Live recap of every action taken during the session + recommended next steps |

### Additional Highlights

- **Auto-Update** — On launch, the app checks GitHub Releases for new versions and offers a one-click in-app upgrade.
- **Privileged Operations** — Uses `pkexec` with a dedicated polkit policy. One auth prompt, no raw terminal commands.
- **Async Execution** — All installs run in background threads with spinner feedback, keeping the UI responsive.
- **No Zorin Branding** — Branded as "First Steps" with app ID `io.github.firststeps` to stay trademark-clean.

---

## Legal & Licensing

This project is licensed under the **GNU General Public License v3.0 or later**.

- A copy of the license is available in the [LICENSE](LICENSE) file.
- The application icon is original work created for this project and is also licensed under GPL-3.0-or-later.
- This project is not affiliated with or endorsed by Zorin Group. All branding is original to "First Steps" to avoid trademark infringement.
- For a full list of dependencies and their licenses, see the [NOTICE](NOTICE) file.
- A comprehensive licensing audit is available in [LICENSING-AUDIT.md](LICENSING-AUDIT.md).

## Contributing

Contributions are welcome! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines on reporting bugs, suggesting features, and submitting code.

## Development

The application is written in Python using the PyGObject bindings for GTK4 and Libadwaita.

| Component | Path |
|-----------|------|
| Main Application | `first_steps/app.py` |
| Auto-Update Module | `first_steps/updater.py` |
| UI Pages | `first_steps/pages/` |
| Base Page Class | `first_steps/pages/__init__.py` |
| Privileged Helper | `scripts/first-steps-helper` |
| Polkit Policy | `data/io.github.firststeps.policy` |
| Install Script | `install.sh` |
| .deb Build Script | `packaging/build-deb.sh` |
| Online Installer | `scripts/install-online.sh` |

To run from the source tree without installing:

```bash
./first-steps
```

To rebuild the .deb package:

```bash
./packaging/build-deb.sh
```

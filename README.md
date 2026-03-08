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
wget https://github.com/Naftaliro/first-steps/releases/latest/download/first-steps_1.0.0-1_all.deb
sudo apt install ./first-steps_1.0.0-1_all.deb
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

- **Codecs & Media**: One-click install of `ubuntu-restricted-extras`, GStreamer plugins, DVD support, and hardware video acceleration.
- **Flatpak/Flathub**: Enables the Flathub remote if not already active and provides a curated app picker for popular software like VLC, Bottles, OBS, and more.
- **Driver Detection**: Wraps the `ubuntu-drivers devices` output and lets the user install recommended drivers with a single click.
- **Windows App Compatibility**: Installs and pre-configures Bottles, the modern Wine frontend, with a guided first-bottle setup.
- **Backup Setup**: Configures Timeshift with sane defaults (weekly snapshots, keep 3) in two clicks.
- **Power & Performance**: Visually set the default power mode, lid close behavior, and auto-suspend timeouts.
- **Firewall**: Enable and configure UFW (Uncomplicated Firewall) with sensible defaults and easy service exceptions.
- **Extras**: A collection of useful additions, including:
    - An installer for the [GNOME Theme Switcher](https://github.com/Naftaliro/gnome-theme-switcher)
    - A one-click system update button
    - Accessibility quick-toggles (Large Text, High Contrast, Large Cursor, Reduce Animations)
    - An installer for handy utilities like `gnome-tweaks`, `htop`, and `git`

---

## Legal & Licensing

This project is licensed under the **GNU General Public License v3.0 or later**.

- A copy of the license is available in the [LICENSE](LICENSE) file.
- The application icon is original work created for this project and is also licensed under GPL-3.0-or-later.
- This project is not affiliated with or endorsed by Zorin Group. All branding is original to "First Steps" to avoid trademark infringement.
- For a full list of dependencies and their licenses, see the [NOTICE](NOTICE) file.
- A comprehensive licensing audit is available in [LICENSING-AUDIT.md](LICENSING-AUDIT.md).

## Development

The application is written in Python using the PyGObject bindings for GTK4 and Libadwaita.

| Component | Path |
|-----------|------|
| Main Application | `first_steps/app.py` |
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

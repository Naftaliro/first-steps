# First Steps — Onboarding Wizard for Zorin OS

![First Steps Icon](data/icons/hicolor/scalable/apps/io.github.firststeps.svg)

A GTK4 + LibAdwaita "First Steps" app for Zorin OS 18 and other Ubuntu-based systems. Think of it like a welcome wizard that actually *does things*, not just shows links. This project applies the philosophy of a simple, powerful UI to the full system onboarding problem.

This application provides a clean, checkbox-driven interface to handle essential setup tasks without ever touching a terminal.

## Features

- **Codecs & Media**: One-click install of `ubuntu-restricted-extras`, GStreamer plugins, and DVD support.
- **Flatpak/Flathub**: Enables the Flathub remote if not already active and provides a curated app picker for popular software like VLC, Bottles, OBS, and more.
- **Driver Detection**: Wraps the `ubuntu-drivers devices` output and lets the user install recommended drivers with a single click.
- **Windows App Compatibility**: Installs and pre-configures Bottles, the modern Wine frontend, with a guided first-bottle setup.
- **Backup Setup**: Configures Timeshift with sane defaults (weekly snapshots, keep 3) in two clicks.
- **Power & Performance**: Visually set the default power mode, lid close behavior, and auto-suspend timeouts.
- **Firewall**: Enable and configure UFW (Uncomplicated Firewall) with sensible defaults and easy service exceptions.
- **Extras**: A collection of useful additions, including:
    - An installer for the [GNOME Theme Switcher](https://github.com/Naftaliro/gnome-theme-switcher)
    - A one-click system update button
    - Accessibility quick-toggles (Large Text, High Contrast, etc.)
    - An installer for handy utilities like `gnome-tweaks`, `htop`, and `git`.

## Installation

1.  **Clone the repository:**

    ```bash
    git clone https://github.com/Naftaliro/first-steps.git
    cd first-steps
    ```

2.  **Run the installer:**

    The script will check for dependencies (like `python3-gi`, `gir1.2-adw-1`, `flatpak`) and install them if missing. It will then install the application files, desktop entry, and icon system-wide.

    ```bash
    sudo ./install.sh
    ```

3.  **Launch the application:**

    You can find "First Steps" in your application menu or run it from the terminal:

    ```bash
    first-steps
    ```

### Uninstallation

To remove the application, run the install script with the `remove` argument:

```bash
sudo ./install.sh remove
```

## Legal & Licensing

This project is licensed under the **GNU General Public License v3.0 or later**.

- A copy of the license is available in the [LICENSE](LICENSE) file.
- The application icon is original work created for this project and is also licensed under GPL-3.0-or-later.
- This project is not affiliated with or endorsed by Zorin Group. All branding is original to "First Steps" to avoid trademark infringement.
- For a full list of dependencies and their licenses, see the [NOTICE](NOTICE) file.

## Development

The application is written in Python using the PyGObject bindings for GTK4 and Libadwaita. The UI is constructed programmatically.

- **Main Application**: `first_steps/app.py`
- **UI Pages**: `first_steps/pages/`
- **Privileged Helper**: `scripts/first-steps-helper` (called via `pkexec`)
- **Polkit Policy**: `data/io.github.firststeps.policy`
- **Installation Script**: `install.sh`

To run from the source tree without installing, execute the main package directory:

```bash
./first_steps
```

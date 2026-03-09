# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright 2026 Naftali Rosen
"""Extras page — theme switcher, system update, accessibility, and more."""

import os
import subprocess

import gi

gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")

from gi.repository import Adw, GLib, Gtk

from first_steps.pages import BasePage


# GitHub repos for the theme switcher
THEME_SWITCHER_REPO = "https://github.com/Naftaliro/gnome-theme-switcher.git"
THEME_PACK_REPO = "https://github.com/Naftaliro/zorinos-gnome-themes.git"


class ExtrasPage(BasePage):
    PAGE_TAG = "extras"
    PAGE_TITLE = "Extras"

    def build_ui(self) -> None:
        self.add_status_page(
            "applications-utilities-symbolic",
            "Extras",
            "A few more things to round out your setup."
        )

        # ── Theme Switcher ───────────────────────────────────────────
        self._theme_group = self.add_preferences_group(
            "GNOME Theme Switcher",
            "Install the terminal-based theme switcher with 9+ built-in themes "
            "for a fully customized desktop look."
        )

        theme_row = Adw.ActionRow()
        theme_row.set_title("GNOME Theme Switcher")
        theme_row.set_subtitle(
            "TUI for switching system-wide GNOME themes \u2014 zero dependencies, "
            "macOS/Windows styles, and more"
        )
        theme_row.add_prefix(Gtk.Image.new_from_icon_name("preferences-desktop-theme-symbolic"))

        self._theme_btn = Gtk.Button(label="Install")
        self._theme_btn.add_css_class("suggested-action")
        self._theme_btn.set_valign(Gtk.Align.CENTER)
        self._theme_btn.connect("clicked", self._on_install_theme_switcher)
        theme_row.add_suffix(self._theme_btn)
        self._theme_group.add(theme_row)

        theme_pack_row = Adw.ActionRow()
        theme_pack_row.set_title("Theme Packs (macOS, Windows, etc.)")
        theme_pack_row.set_subtitle(
            "Pre-built theme install scripts for popular desktop styles"
        )
        theme_pack_row.add_prefix(Gtk.Image.new_from_icon_name("preferences-color-symbolic"))

        self._theme_pack_btn = Gtk.Button(label="Install")
        self._theme_pack_btn.set_valign(Gtk.Align.CENTER)
        self._theme_pack_btn.connect("clicked", self._on_install_theme_packs)
        theme_pack_row.add_suffix(self._theme_pack_btn)
        self._theme_group.add(theme_pack_row)

        # ── System Update ────────────────────────────────────────────
        self._update_group = self.add_preferences_group(
            "System Update",
            "Check for and install available system updates."
        )

        self._update_row = Adw.ActionRow()
        self._update_row.set_title("Update System Packages")
        self._update_row.set_subtitle("Run apt update && apt upgrade")
        self._update_row.add_prefix(
            Gtk.Image.new_from_icon_name("software-update-available-symbolic")
        )

        self._update_btn = Gtk.Button(label="Update Now")
        self._update_btn.set_valign(Gtk.Align.CENTER)
        self._update_btn.add_css_class("suggested-action")
        self._update_btn.connect("clicked", self._on_system_update)
        self._update_row.add_suffix(self._update_btn)
        self._update_group.add(self._update_row)

        # ── Accessibility ────────────────────────────────────────────
        self._a11y_group = self.add_preferences_group(
            "Accessibility Quick Settings",
            "Common accessibility tweaks:"
        )

        self._large_text_row, self._large_text_switch = self.add_action_row_with_switch(
            self._a11y_group,
            "Large Text",
            "Increase the default text size for better readability",
            active=False,
        )
        self._large_text_switch.connect("notify::active", self._on_large_text_toggled)

        self._high_contrast_row, self._high_contrast_switch = self.add_action_row_with_switch(
            self._a11y_group,
            "High Contrast",
            "Enable high-contrast mode for better visibility",
            active=False,
        )
        self._high_contrast_switch.connect("notify::active", self._on_high_contrast_toggled)

        self._cursor_size_row, self._cursor_size_switch = self.add_action_row_with_switch(
            self._a11y_group,
            "Large Cursor",
            "Increase cursor size for easier tracking",
            active=False,
        )
        self._cursor_size_switch.connect("notify::active", self._on_cursor_size_toggled)

        self._reduce_motion_row, self._reduce_motion_switch = self.add_action_row_with_switch(
            self._a11y_group,
            "Reduce Animations",
            "Minimize window animations and transitions",
            active=False,
        )
        self._reduce_motion_switch.connect("notify::active", self._on_reduce_motion_toggled)

        # ── Useful Utilities ─────────────────────────────────────────
        self._utils_group = self.add_preferences_group(
            "Useful Utilities",
            "Handy system tools you might want:"
        )

        self._util_checks: dict[str, Gtk.CheckButton] = {}

        utils = [
            ("gnome-tweaks", "GNOME Tweaks",
             "Advanced GNOME desktop settings"),
            ("dconf-editor", "dconf Editor",
             "Low-level configuration editor"),
            ("synaptic", "Synaptic Package Manager",
             "Full-featured graphical package manager"),
            ("htop", "htop",
             "Interactive process viewer for the terminal"),
            ("neofetch", "Neofetch",
             "System info display for the terminal"),
            ("tldr", "tldr",
             "Simplified man pages \u2014 community-driven help"),
            ("curl", "curl",
             "Command-line HTTP client"),
            ("git", "Git",
             "Version control system"),
        ]

        for pkg, name, desc in utils:
            row, check = self.add_action_row_with_check(
                self._utils_group, name, desc, active=False
            )
            self._util_checks[pkg] = check

        # Install utilities button
        self._util_btn = Gtk.Button(label="Install Selected Utilities")
        self._util_btn.add_css_class("suggested-action")
        self._util_btn.set_halign(Gtk.Align.CENTER)
        self._util_btn.set_margin_top(8)
        self._util_btn.connect("clicked", self._on_install_utils)
        self._outer_box.append(self._util_btn)

        # Progress
        self._progress_label = Gtk.Label()
        self._progress_label.set_xalign(0)
        self._progress_label.set_wrap(True)
        self._progress_label.add_css_class("dim-label")
        self._progress_label.set_visible(False)
        self._outer_box.append(self._progress_label)

        self.add_navigation_buttons(back_tag="firewall", next_tag="summary")

        # Detect current a11y settings
        GLib.idle_add(self._detect_a11y_settings)

    # ── Theme Switcher ───────────────────────────────────────────────
    def _on_install_theme_switcher(self, btn: Gtk.Button) -> None:
        btn.set_sensitive(False)
        btn.set_label("Installing...")
        self._progress_label.set_text("Cloning and installing GNOME Theme Switcher...")
        self._progress_label.set_visible(True)

        self.run_unprivileged(
            ["bash", "-c",
             f"cd /tmp && rm -rf gnome-theme-switcher && "
             f"git clone {THEME_SWITCHER_REPO} && "
             f"cd gnome-theme-switcher && "
             f"chmod +x install.sh && ./install.sh"],
            success_msg="Installed GNOME Theme Switcher",
            callback=lambda s, o: self._on_theme_installed(s, o, btn),
        )

    def _on_theme_installed(self, success: bool, output: str, btn: Gtk.Button) -> None:
        if success:
            btn.set_label("Installed")
            self._progress_label.set_text(
                "Theme Switcher installed! Run 'theme-switcher' in your terminal."
            )
            self.show_toast("Theme Switcher installed!")
        else:
            btn.set_label("Retry")
            btn.set_sensitive(True)
            self._progress_label.set_text(f"Installation failed.\n{output[:200]}")

    def _on_install_theme_packs(self, btn: Gtk.Button) -> None:
        btn.set_sensitive(False)
        btn.set_label("Installing...")
        self._progress_label.set_text("Cloning theme packs repository...")
        self._progress_label.set_visible(True)

        self.run_unprivileged(
            ["bash", "-c",
             f"cd /tmp && rm -rf zorinos-gnome-themes && "
             f"git clone {THEME_PACK_REPO} && "
             f"echo 'Theme packs cloned to /tmp/zorinos-gnome-themes'"],
            success_msg="Downloaded GNOME theme packs",
            callback=lambda s, o: self._on_packs_installed(s, o, btn),
        )

    def _on_packs_installed(self, success: bool, output: str, btn: Gtk.Button) -> None:
        if success:
            btn.set_label("Downloaded")
            self._progress_label.set_text(
                "Theme packs downloaded! Check /tmp/zorinos-gnome-themes for install scripts."
            )
            self.show_toast("Theme packs downloaded!")
        else:
            btn.set_label("Retry")
            btn.set_sensitive(True)
            self._progress_label.set_text(f"Download failed.\n{output[:200]}")

    # ── System Update ────────────────────────────────────────────────
    def _on_system_update(self, btn: Gtk.Button) -> None:
        btn.set_sensitive(False)
        btn.set_label("Updating...")
        self._progress_label.set_text("Running system update... This may take a while.")
        self._progress_label.set_visible(True)

        script_path = "/tmp/first-steps-update.sh"
        script_lines = [
            "#!/bin/bash",
            "set -e",
            "export DEBIAN_FRONTEND=noninteractive",
            "apt-get update",
            "apt-get upgrade -y",
            "apt-get autoremove -y",
        ]
        try:
            with open(script_path, "w") as f:
                f.write("\n".join(script_lines) + "\n")
            os.chmod(script_path, 0o755)
        except Exception as e:
            self._progress_label.set_text(f"Error: {e}")
            btn.set_sensitive(True)
            btn.set_label("Update Now")
            return

        self.run_privileged(
            ["bash", script_path],
            success_msg="System packages updated",
            callback=lambda s, o: self._on_update_done(s, o, btn),
        )

    def _on_update_done(self, success: bool, output: str, btn: Gtk.Button) -> None:
        if success:
            btn.set_label("Updated")
            self._progress_label.set_text("System is up to date!")
            self.show_toast("System updated!")
        else:
            btn.set_label("Retry")
            btn.set_sensitive(True)
            short = output.strip().split("\n")[-3:]
            self._progress_label.set_text(
                "Update encountered issues:\n" + "\n".join(short)
            )

    # ── Accessibility ────────────────────────────────────────────────
    def _detect_a11y_settings(self) -> None:
        """Detect current accessibility settings."""
        try:
            result = subprocess.run(
                ["gsettings", "get", "org.gnome.desktop.interface", "text-scaling-factor"],
                capture_output=True, text=True, timeout=5,
            )
            if result.returncode == 0:
                factor = float(result.stdout.strip())
                self._large_text_switch.set_active(factor > 1.1)
        except Exception:
            pass

        try:
            result = subprocess.run(
                ["gsettings", "get", "org.gnome.desktop.interface", "cursor-size"],
                capture_output=True, text=True, timeout=5,
            )
            if result.returncode == 0:
                size = int(result.stdout.strip())
                self._cursor_size_switch.set_active(size > 30)
        except Exception:
            pass

    def _gsettings_set(self, schema: str, key: str, value: str) -> None:
        """Helper to set a gsettings value without blocking."""
        try:
            subprocess.Popen(
                ["gsettings", "set", schema, key, value],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
        except Exception:
            pass

    def _on_large_text_toggled(self, switch, _) -> None:
        factor = "1.25" if switch.get_active() else "1.0"
        self._gsettings_set(
            "org.gnome.desktop.interface", "text-scaling-factor", factor
        )
        self.window.log_action(f"Set text scaling to {factor}")

    def _on_high_contrast_toggled(self, switch, _) -> None:
        theme = "HighContrast" if switch.get_active() else "Adwaita"
        self._gsettings_set("org.gnome.desktop.interface", "gtk-theme", theme)
        self.window.log_action(f"Set GTK theme to {theme}")

    def _on_cursor_size_toggled(self, switch, _) -> None:
        size = "48" if switch.get_active() else "24"
        self._gsettings_set("org.gnome.desktop.interface", "cursor-size", size)
        self.window.log_action(f"Set cursor size to {size}")

    def _on_reduce_motion_toggled(self, switch, _) -> None:
        enabled = "false" if switch.get_active() else "true"
        self._gsettings_set(
            "org.gnome.desktop.interface", "enable-animations", enabled
        )
        action = "Reduced" if switch.get_active() else "Restored"
        self.window.log_action(f"{action} animations")

    # ── Utilities ────────────────────────────────────────────────────
    def _on_install_utils(self, btn: Gtk.Button) -> None:
        selected = [
            pkg for pkg, check in self._util_checks.items()
            if check.get_active()
        ]
        if not selected:
            self._progress_label.set_text("No utilities selected.")
            self._progress_label.set_visible(True)
            return

        btn.set_sensitive(False)
        self._progress_label.set_text(f"Installing: {', '.join(selected)}...")
        self._progress_label.set_visible(True)

        script_path = "/tmp/first-steps-utils.sh"
        script_lines = [
            "#!/bin/bash",
            "set -e",
            "export DEBIAN_FRONTEND=noninteractive",
            f"apt-get install -y {' '.join(selected)}",
        ]
        try:
            with open(script_path, "w") as f:
                f.write("\n".join(script_lines) + "\n")
            os.chmod(script_path, 0o755)
        except Exception as e:
            self._progress_label.set_text(f"Error: {e}")
            btn.set_sensitive(True)
            return

        self.run_privileged(
            ["bash", script_path],
            success_msg=f"Installed utilities: {', '.join(selected)}",
            callback=lambda s, o: self._on_utils_done(s, o, btn),
        )

    def _on_utils_done(self, success: bool, output: str, btn: Gtk.Button) -> None:
        btn.set_sensitive(True)
        if success:
            self._progress_label.set_text("Utilities installed successfully!")
            self.show_toast("Utilities installed!")
        else:
            short = output.strip().split("\n")[-3:]
            self._progress_label.set_text(
                "Some installs may have failed:\n" + "\n".join(short)
            )

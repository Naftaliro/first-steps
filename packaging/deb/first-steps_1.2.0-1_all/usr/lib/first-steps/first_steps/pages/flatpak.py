# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright 2026 Naftali
"""Flatpak & Apps page — enable Flathub and install curated applications."""

import gi
import subprocess

gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")

from gi.repository import Adw, GLib, Gtk

from first_steps.pages import BasePage


# Curated app list: (flatpak_id, display_name, description, category)
CURATED_APPS = [
    # Media
    ("org.videolan.VLC", "VLC Media Player",
     "The Swiss-army-knife media player", "Media"),
    ("com.obsproject.Studio", "OBS Studio",
     "Screen recording and live streaming", "Media"),
    ("org.gimp.GIMP", "GIMP",
     "Professional image editor", "Media"),
    ("org.audacityteam.Audacity", "Audacity",
     "Audio editor and recorder", "Media"),
    ("org.kde.kdenlive", "Kdenlive",
     "Professional video editor", "Media"),
    # Productivity
    ("org.libreoffice.LibreOffice", "LibreOffice",
     "Full office suite", "Productivity"),
    ("md.obsidian.Obsidian", "Obsidian",
     "Knowledge base and note-taking", "Productivity"),
    ("com.bitwarden.desktop", "Bitwarden",
     "Open-source password manager", "Productivity"),
    # Internet
    ("org.mozilla.firefox", "Firefox",
     "Privacy-focused web browser", "Internet"),
    ("com.brave.Browser", "Brave Browser",
     "Privacy-first Chromium browser", "Internet"),
    ("org.signal.Signal", "Signal",
     "Private messenger", "Internet"),
    # Gaming & Compatibility
    ("com.usebottles.bottles", "Bottles",
     "Run Windows software and games", "Gaming"),
    ("com.valvesoftware.Steam", "Steam",
     "PC gaming platform", "Gaming"),
    ("net.lutris.Lutris", "Lutris",
     "Open gaming platform", "Gaming"),
    # Development
    ("com.visualstudio.code", "VS Code",
     "Popular code editor", "Development"),
    ("io.podman_desktop.PodmanDesktop", "Podman Desktop",
     "Container management", "Development"),
]


class FlatpakPage(BasePage):
    PAGE_TAG = "flatpak"
    PAGE_TITLE = "Flatpak & Apps"

    def build_ui(self) -> None:
        self.add_status_page(
            "system-software-install-symbolic",
            "Flatpak & Apps",
            "Flatpak gives you access to thousands of apps from Flathub, "
            "sandboxed and always up to date."
        )

        # Flathub status
        self._flathub_group = self.add_preferences_group(
            "Flathub Repository",
            "Flathub is the main source of Flatpak applications."
        )

        self._flathub_status_row = Adw.ActionRow()
        self._flathub_status_row.set_title("Flathub Status")
        self._flathub_status_row.set_subtitle("Checking...")
        self._flathub_group.add(self._flathub_status_row)

        self._enable_flathub_btn = Gtk.Button(label="Enable Flathub")
        self._enable_flathub_btn.add_css_class("suggested-action")
        self._enable_flathub_btn.set_valign(Gtk.Align.CENTER)
        self._enable_flathub_btn.connect("clicked", self._on_enable_flathub)
        self._enable_flathub_btn.set_visible(False)
        self._flathub_status_row.add_suffix(self._enable_flathub_btn)

        # Check Flathub status on load
        GLib.idle_add(self._check_flathub_status)

        # Curated apps grouped by category
        self._app_checks: dict[str, Gtk.CheckButton] = {}
        categories = {}
        for app_id, name, desc, cat in CURATED_APPS:
            categories.setdefault(cat, []).append((app_id, name, desc))

        for cat_name, apps in categories.items():
            group = self.add_preferences_group(cat_name)
            for app_id, name, desc in apps:
                row, check = self.add_action_row_with_check(
                    group, name, desc, active=False
                )
                self._app_checks[app_id] = check

        # Status area
        self._status_group = self.add_preferences_group("Installation Status")
        self._status_label = Gtk.Label(label="Select apps above, then click Install.")
        self._status_label.set_xalign(0)
        self._status_label.add_css_class("dim-label")
        self._status_label.set_wrap(True)
        row = Adw.ActionRow()
        row.set_child(self._status_label)
        self._status_group.add(row)

        # Install button
        btn_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=12)
        btn_box.set_halign(Gtk.Align.CENTER)
        btn_box.set_margin_top(8)

        self._install_btn = Gtk.Button(label="Install Selected Apps")
        self._install_btn.add_css_class("suggested-action")
        self._install_btn.connect("clicked", self._on_install_apps)
        btn_box.append(self._install_btn)

        self._spinner = Gtk.Spinner()
        self._spinner.set_visible(False)
        btn_box.append(self._spinner)
        self._outer_box.append(btn_box)

        self.add_navigation_buttons(back_tag="codecs", next_tag="drivers")

    def _check_flathub_status(self) -> None:
        """Check if Flathub remote is already configured."""
        try:
            result = subprocess.run(
                ["flatpak", "remotes", "--columns=name"],
                capture_output=True, text=True, timeout=10,
            )
            remotes = result.stdout.strip().split("\n")
            if "flathub" in [r.strip() for r in remotes]:
                self._flathub_status_row.set_subtitle("Flathub is enabled and ready")
                self._flathub_status_row.add_prefix(
                    Gtk.Image.new_from_icon_name("emblem-ok-symbolic")
                )
                self._enable_flathub_btn.set_visible(False)
            else:
                self._flathub_status_row.set_subtitle("Flathub is not configured")
                self._enable_flathub_btn.set_visible(True)
        except Exception:
            self._flathub_status_row.set_subtitle("Could not detect Flatpak status")
            self._enable_flathub_btn.set_visible(True)

    def _on_enable_flathub(self, btn: Gtk.Button) -> None:
        btn.set_sensitive(False)
        self._flathub_status_row.set_subtitle("Enabling Flathub...")

        self.run_unprivileged(
            [
                "flatpak", "remote-add", "--if-not-exists", "--user",
                "flathub", "https://dl.flathub.org/repo/flathub.flatpakrepo",
            ],
            success_msg="Enabled Flathub repository",
            callback=self._on_flathub_enabled,
        )

    def _on_flathub_enabled(self, success: bool, output: str) -> None:
        if success:
            self._flathub_status_row.set_subtitle("Flathub is now enabled!")
            self._enable_flathub_btn.set_visible(False)
        else:
            # Try system-wide if user install failed
            self.run_privileged(
                [
                    "flatpak", "remote-add", "--if-not-exists",
                    "flathub", "https://dl.flathub.org/repo/flathub.flatpakrepo",
                ],
                success_msg="Enabled Flathub repository (system-wide)",
                callback=lambda s, o: self._flathub_status_row.set_subtitle(
                    "Flathub enabled (system-wide)" if s else f"Error: {o[:100]}"
                ),
            )

    def _on_install_apps(self, btn: Gtk.Button) -> None:
        selected = [
            app_id for app_id, check in self._app_checks.items()
            if check.get_active()
        ]
        if not selected:
            self._status_label.set_text("No apps selected. Check at least one app above.")
            return

        self._install_btn.set_sensitive(False)
        self._spinner.set_visible(True)
        self._spinner.start()

        names = []
        for app_id, name, _, _ in CURATED_APPS:
            if app_id in selected:
                names.append(name)
        self._status_label.set_text(f"Installing {len(selected)} app(s): {', '.join(names)}...")

        cmd = ["flatpak", "install", "--user", "-y", "flathub"] + selected

        self.run_unprivileged(
            cmd,
            success_msg=f"Installed Flatpak apps: {', '.join(names)}",
            callback=self._on_apps_installed,
        )

    def _on_apps_installed(self, success: bool, output: str) -> None:
        self._spinner.stop()
        self._spinner.set_visible(False)
        self._install_btn.set_sensitive(True)

        if success:
            self._status_label.set_text("All selected apps installed successfully!")
            self.show_toast("Flatpak apps installed!")
        else:
            short = output.strip().split("\n")[-3:]
            self._status_label.set_text(
                "Some apps may have failed to install:\n" + "\n".join(short)
            )

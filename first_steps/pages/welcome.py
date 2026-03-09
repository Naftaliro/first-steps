# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright 2026 Naftali Rosen
"""Welcome page — the landing screen for the onboarding wizard."""

import gi

gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")

from gi.repository import Adw, Gtk

from first_steps.pages import BasePage


class WelcomePage(BasePage):
    PAGE_TAG = "welcome"
    PAGE_TITLE = "Welcome"
    PAGE_ICON = "go-home-symbolic"

    def build_ui(self) -> None:
        # Hero status page
        status = Adw.StatusPage()
        status.set_icon_name("preferences-system-symbolic")
        status.set_title("Welcome to First Steps")
        status.set_description(
            "Your system is almost ready. This wizard will help you install "
            "media codecs, set up Flatpak, detect drivers, configure backups, "
            "and more — all without touching a terminal.\n\n"
            "Work through each section at your own pace, or skip anything "
            "you don't need. Everything here is optional."
        )
        self._outer_box.append(status)

        # Quick-start group
        group = self.add_preferences_group(
            "Quick Overview",
            "Here's what we can help you set up today:"
        )

        items = [
            ("media-playback-start-symbolic", "Codecs & Media",
             "Play any video or audio format out of the box"),
            ("system-software-install-symbolic", "Flatpak & Apps",
             "Enable Flathub and install popular applications"),
            ("preferences-system-symbolic", "Drivers",
             "Detect and install recommended hardware drivers"),
            ("preferences-desktop-apps-symbolic", "Windows Apps",
             "Run Windows software via Bottles"),
            ("drive-harddisk-symbolic", "Backup",
             "Set up automatic system snapshots with Timeshift"),
            ("battery-symbolic", "Power",
             "Configure power profiles and lid behavior"),
            ("security-high-symbolic", "Firewall",
             "Enable and configure UFW firewall"),
            ("applications-utilities-symbolic", "Extras",
             "Theme switcher, system updates, and more"),
        ]

        for icon, title, subtitle in items:
            row = Adw.ActionRow()
            row.set_title(title)
            row.set_subtitle(subtitle)
            row.add_prefix(Gtk.Image.new_from_icon_name(icon))
            group.add(row)

        # Get started button
        self.add_navigation_buttons(next_tag="codecs")

        # Version label
        from first_steps import __version__
        ver_label = Gtk.Label(label=f"First Steps v{__version__}")
        ver_label.add_css_class("dim-label")
        ver_label.add_css_class("caption")
        ver_label.set_margin_top(8)
        self._outer_box.append(ver_label)

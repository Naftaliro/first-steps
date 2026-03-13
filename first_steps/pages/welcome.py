# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright 2026 Naftali
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
        # ── Hero icon ────────────────────────────────────────────────
        icon = Gtk.Image.new_from_icon_name("preferences-system-symbolic")
        icon.set_pixel_size(96)
        icon.add_css_class("dim-label")
        icon.set_margin_top(16)
        icon.set_margin_bottom(8)
        icon.set_halign(Gtk.Align.CENTER)
        self._outer_box.append(icon)

        # ── Title ────────────────────────────────────────────────────
        title_label = Gtk.Label(label="Welcome to First Steps")
        title_label.add_css_class("title-1")
        title_label.set_halign(Gtk.Align.CENTER)
        title_label.set_margin_bottom(4)
        self._outer_box.append(title_label)

        # ── Description — full-width inline text, no subscroll ───────
        desc_text = (
            "Your system is almost ready. This wizard will help you "
            "install media codecs, set up Flatpak, detect drivers, "
            "configure backups, and more — all without touching a "
            "terminal.\n\n"
            "Work through each section at your own pace using the "
            "sidebar, or skip anything you don't need. Everything "
            "here is completely optional."
        )
        desc_label = Gtk.Label(label=desc_text)
        desc_label.set_wrap(True)
        desc_label.set_wrap_mode(2)  # WORD_CHAR
        desc_label.set_xalign(0)
        desc_label.set_halign(Gtk.Align.FILL)
        desc_label.add_css_class("body")
        desc_label.set_margin_start(4)
        desc_label.set_margin_end(4)
        desc_label.set_margin_bottom(8)
        self._outer_box.append(desc_label)

        # ── Separator ────────────────────────────────────────────────
        sep = Gtk.Separator(orientation=Gtk.Orientation.HORIZONTAL)
        sep.set_margin_top(4)
        sep.set_margin_bottom(4)
        self._outer_box.append(sep)

        # ── Quick overview — inline cards, all part of the same
        #    scroll as the rest of the page ───────────────────────────
        overview_title = Gtk.Label(label="What We Can Help You Set Up")
        overview_title.add_css_class("title-3")
        overview_title.set_halign(Gtk.Align.START)
        overview_title.set_margin_start(4)
        overview_title.set_margin_top(4)
        self._outer_box.append(overview_title)

        overview_desc = Gtk.Label(
            label="Each section handles a different part of your system setup:"
        )
        overview_desc.set_wrap(True)
        overview_desc.set_xalign(0)
        overview_desc.add_css_class("dim-label")
        overview_desc.set_margin_start(4)
        overview_desc.set_margin_bottom(8)
        self._outer_box.append(overview_desc)

        # Build the overview items as a PreferencesGroup for clean styling
        group = Adw.PreferencesGroup()
        self._outer_box.append(group)

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

        for icon_name, row_title, subtitle in items:
            row = Adw.ActionRow()
            row.set_title(row_title)
            row.set_subtitle(subtitle)
            row.add_prefix(Gtk.Image.new_from_icon_name(icon_name))
            # Add a go-next indicator to hint these are navigable sections
            arrow = Gtk.Image.new_from_icon_name("go-next-symbolic")
            arrow.add_css_class("dim-label")
            row.add_suffix(arrow)
            group.add(row)

        # ── Get started button ───────────────────────────────────────
        get_started_btn = Gtk.Button(label="Get Started  \u2192")
        get_started_btn.add_css_class("suggested-action")
        get_started_btn.add_css_class("pill")
        get_started_btn.set_halign(Gtk.Align.CENTER)
        get_started_btn.set_margin_top(16)
        get_started_btn.set_margin_bottom(8)
        get_started_btn.connect(
            "clicked", lambda _: self.window.navigate_to("codecs")
        )
        self._outer_box.append(get_started_btn)

        # ── Version label ────────────────────────────────────────────
        from first_steps import __version__
        ver_label = Gtk.Label(label=f"First Steps v{__version__}")
        ver_label.add_css_class("dim-label")
        ver_label.add_css_class("caption")
        ver_label.set_margin_top(4)
        ver_label.set_margin_bottom(8)
        self._outer_box.append(ver_label)

# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright 2026 Naftali Rosen
"""Summary page — recap of all completed actions, export report, and next steps."""

import datetime
import os

import gi

gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")

from gi.repository import Adw, GLib, Gtk

from first_steps.pages import BasePage


class SummaryPage(BasePage):
    PAGE_TAG = "summary"
    PAGE_TITLE = "Summary"
    SKIPPABLE = False

    def build_ui(self) -> None:
        self._status = Adw.StatusPage()
        self._status.set_icon_name("emblem-ok-symbolic")
        self._status.set_title("All Done!")
        self._status.set_description(
            "Here's a summary of everything that was configured during this session."
        )
        self._outer_box.append(self._status)

        # Completed actions group
        self._actions_group = self.add_preferences_group(
            "Completed Actions",
            "Everything you set up today:"
        )

        self._action_rows: list[Adw.ActionRow] = []
        self._showing_no_actions = False

        self._no_actions_row = Adw.ActionRow()
        self._no_actions_row.set_title("No actions completed yet")
        self._no_actions_row.set_subtitle(
            "Go through the wizard pages to configure your system"
        )
        self._actions_group.add(self._no_actions_row)
        self._showing_no_actions = True

        # Button row: Refresh + Export
        btn_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=12)
        btn_box.set_halign(Gtk.Align.CENTER)

        refresh_btn = Gtk.Button(label="Refresh Summary")
        refresh_btn.connect("clicked", self._refresh)
        btn_box.append(refresh_btn)

        export_btn = Gtk.Button(label="Export Report")
        export_btn.set_icon_name("document-save-symbolic")
        export_btn.add_css_class("suggested-action")
        export_btn.connect("clicked", self._on_export)
        btn_box.append(export_btn)

        self._outer_box.append(btn_box)

        # Next steps
        self._next_group = self.add_preferences_group("Recommended Next Steps")

        next_steps = [
            ("dialog-information-symbolic", "Reboot if drivers were installed",
             "Some hardware drivers require a reboot to take effect"),
            ("preferences-desktop-theme-symbolic", "Customize your desktop",
             "Try the GNOME Theme Switcher for a fresh look"),
            ("software-update-available-symbolic", "Keep your system updated",
             "Run system updates regularly for security and stability"),
            ("drive-harddisk-symbolic", "Verify your first backup",
             "Open Timeshift to confirm your snapshot was created"),
            ("web-browser-symbolic", "Explore Flathub",
             "Visit flathub.org to discover more applications"),
        ]

        for icon, title, subtitle in next_steps:
            row = Adw.ActionRow()
            row.set_title(title)
            row.set_subtitle(subtitle)
            row.add_prefix(Gtk.Image.new_from_icon_name(icon))
            self._next_group.add(row)

        # Close button
        close_btn = Gtk.Button(label="Close First Steps")
        close_btn.add_css_class("destructive-action")
        close_btn.set_halign(Gtk.Align.CENTER)
        close_btn.set_margin_top(16)
        close_btn.connect("clicked", self._on_close)
        self._outer_box.append(close_btn)

        self.add_navigation_buttons(back_tag="extras", skip=False)

        # Auto-refresh when page becomes visible
        self.connect("map", lambda w: self._refresh(None))

    def _refresh(self, btn) -> None:
        """Refresh the list of completed actions."""
        for row in self._action_rows:
            self._actions_group.remove(row)
        self._action_rows.clear()

        if self._showing_no_actions:
            self._actions_group.remove(self._no_actions_row)
            self._showing_no_actions = False

        actions = self.window.get_completed_actions()

        if not actions:
            self._actions_group.add(self._no_actions_row)
            self._showing_no_actions = True
            self._status.set_description(
                "No actions were completed. Go through the wizard to set up your system."
            )
        else:
            for i, action in enumerate(actions, 1):
                row = Adw.ActionRow()
                row.set_title(f"{i}. {action}")
                row.add_prefix(
                    Gtk.Image.new_from_icon_name("emblem-ok-symbolic")
                )
                self._actions_group.add(row)
                self._action_rows.append(row)

            self._status.set_description(
                f"You completed {len(actions)} action(s) during this session. "
                f"Your system is looking great!"
            )

    def _on_export(self, btn) -> None:
        """Export a setup report as a Markdown file."""
        actions = self.window.get_completed_actions()
        now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        from first_steps import __version__

        lines = [
            "# First Steps Setup Report",
            f"",
            f"**Generated:** {now}",
            f"**Version:** First Steps v{__version__}",
            "",
            "## Completed Actions",
            "",
        ]

        if actions:
            for i, action in enumerate(actions, 1):
                lines.append(f"{i}. {action}")
        else:
            lines.append("No actions were completed during this session.")

        lines.extend([
            "",
            "## Recommended Next Steps",
            "",
            "- Reboot if drivers were installed",
            "- Customize your desktop with the GNOME Theme Switcher",
            "- Keep your system updated regularly",
            "- Verify your first Timeshift backup",
            "- Explore Flathub for more applications",
            "",
            "---",
            f"*Report generated by First Steps v{__version__}*",
            "",
        ])

        report = "\n".join(lines)

        # Save to user's home directory
        home = os.path.expanduser("~")
        filename = f"first-steps-report-{datetime.datetime.now().strftime('%Y%m%d-%H%M%S')}.md"
        filepath = os.path.join(home, filename)

        try:
            with open(filepath, "w") as f:
                f.write(report)
            self.show_toast(f"Report saved to ~/{filename}")
        except OSError as e:
            self.show_error_dialog("Export Failed", f"Could not save report: {e}")

    def _on_close(self, btn) -> None:
        """Close the application."""
        self.window.close()

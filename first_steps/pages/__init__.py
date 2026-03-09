# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright 2026 First Steps Contributors
"""Base page class for wizard pages."""

import os
import subprocess
import threading

import gi

gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")

from gi.repository import Adw, GLib, Gtk


class BasePage(Gtk.ScrolledWindow):
    """Base class for all wizard pages.

    Provides a scrollable container with a centered clamp and common
    helper methods for building preference-style UIs.
    """

    PAGE_TAG = "base"
    PAGE_TITLE = "Base"
    PAGE_DESCRIPTION = ""
    PAGE_ICON = "dialog-information-symbolic"

    def __init__(self, window, **kwargs) -> None:
        super().__init__(**kwargs)
        self.window = window
        self.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)

        self._clamp = Adw.Clamp()
        self._clamp.set_maximum_size(700)
        self._clamp.set_tightening_threshold(500)

        self._outer_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=24)
        self._outer_box.set_margin_top(24)
        self._outer_box.set_margin_bottom(24)
        self._outer_box.set_margin_start(16)
        self._outer_box.set_margin_end(16)

        self._clamp.set_child(self._outer_box)
        self.set_child(self._clamp)

        self.build_ui()

    def build_ui(self) -> None:
        """Override in subclasses to populate the page."""

    # ── Helpers ──────────────────────────────────────────────────────
    def add_status_page(self, icon: str, title: str, description: str) -> Adw.StatusPage:
        """Add a hero status page at the top."""
        status = Adw.StatusPage()
        status.set_icon_name(icon)
        status.set_title(title)
        status.set_description(description)
        self._outer_box.append(status)
        return status

    def add_preferences_group(self, title: str, description: str = "") -> Adw.PreferencesGroup:
        group = Adw.PreferencesGroup()
        group.set_title(title)
        if description:
            group.set_description(description)
        self._outer_box.append(group)
        return group

    def add_action_row_with_switch(
        self, group: Adw.PreferencesGroup, title: str, subtitle: str = "", active: bool = False
    ) -> tuple[Adw.ActionRow, Gtk.Switch]:
        row = Adw.ActionRow()
        row.set_title(title)
        if subtitle:
            row.set_subtitle(subtitle)

        switch = Gtk.Switch()
        switch.set_valign(Gtk.Align.CENTER)
        switch.set_active(active)
        row.add_suffix(switch)
        row.set_activatable_widget(switch)
        group.add(row)
        return row, switch

    def add_action_row_with_check(
        self, group: Adw.PreferencesGroup, title: str, subtitle: str = "", active: bool = False
    ) -> tuple[Adw.ActionRow, Gtk.CheckButton]:
        row = Adw.ActionRow()
        row.set_title(title)
        if subtitle:
            row.set_subtitle(subtitle)

        check = Gtk.CheckButton()
        check.set_valign(Gtk.Align.CENTER)
        check.set_active(active)
        row.add_prefix(check)
        row.set_activatable_widget(check)
        group.add(row)
        return row, check

    def add_button_row(
        self, label: str, css_class: str = "suggested-action", callback=None
    ) -> Gtk.Button:
        btn = Gtk.Button(label=label)
        btn.add_css_class(css_class)
        btn.set_halign(Gtk.Align.CENTER)
        btn.set_margin_top(8)
        if callback:
            btn.connect("clicked", callback)
        self._outer_box.append(btn)
        return btn

    def add_navigation_buttons(self, back_tag: str | None = None, next_tag: str | None = None):
        """Add Back / Next navigation buttons at the bottom."""
        box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=12)
        box.set_halign(Gtk.Align.CENTER)
        box.set_margin_top(16)

        if back_tag:
            back_btn = Gtk.Button(label="\u2190 Back")
            back_btn.add_css_class("flat")
            back_btn.connect("clicked", lambda _: self.window.navigate_to(back_tag))
            box.append(back_btn)

        if next_tag:
            next_btn = Gtk.Button(label="Next \u2192")
            next_btn.add_css_class("suggested-action")
            next_btn.connect("clicked", lambda _: self.window.navigate_to(next_tag))
            box.append(next_btn)

        self._outer_box.append(box)

    def show_toast(self, message: str) -> None:
        """Show an in-app toast notification via the window's ToastOverlay."""
        self.window.show_toast(message)

    def show_error_dialog(self, title: str, body: str) -> None:
        """Show a modal error dialog."""
        dialog = Adw.MessageDialog.new(self.window, title, body)
        dialog.add_response("ok", "OK")
        dialog.set_default_response("ok")
        dialog.present()

    def run_privileged(self, command: list[str], success_msg: str, callback=None) -> None:
        """Run a command via pkexec asynchronously and report result."""
        full_cmd = ["pkexec"] + command

        def _worker():
            try:
                result = subprocess.run(
                    full_cmd,
                    capture_output=True,
                    text=True,
                    timeout=600,
                )
                success = result.returncode == 0
                output = result.stdout + result.stderr
            except subprocess.TimeoutExpired:
                success = False
                output = "Operation timed out after 10 minutes."
            except FileNotFoundError:
                success = False
                output = "pkexec not found. Is policykit-1 installed?"
            except Exception as e:
                success = False
                output = str(e)

            def _on_done():
                if success and success_msg:
                    self.window.log_action(success_msg)
                if callback:
                    callback(success, output)

            GLib.idle_add(_on_done)

        thread = threading.Thread(target=_worker, daemon=True)
        thread.start()

    def run_unprivileged(self, command: list[str], success_msg: str, callback=None) -> None:
        """Run a command without elevation asynchronously."""

        def _worker():
            try:
                result = subprocess.run(
                    command,
                    capture_output=True,
                    text=True,
                    timeout=600,
                )
                success = result.returncode == 0
                output = result.stdout + result.stderr
            except subprocess.TimeoutExpired:
                success = False
                output = "Operation timed out after 10 minutes."
            except FileNotFoundError:
                success = False
                output = f"Command not found: {command[0]}"
            except Exception as e:
                success = False
                output = str(e)

            def _on_done():
                if success and success_msg:
                    self.window.log_action(success_msg)
                if callback:
                    callback(success, output)

            GLib.idle_add(_on_done)

        thread = threading.Thread(target=_worker, daemon=True)
        thread.start()

    @staticmethod
    def clear_preferences_group(group: Adw.PreferencesGroup) -> None:
        """Safely remove all ActionRow children from a PreferencesGroup."""
        # Collect rows first, then remove (avoids mutation during iteration)
        rows_to_remove = []
        child = group.get_first_child()
        while child:
            # The PreferencesGroup wraps rows in a GtkListBox inside a GtkBox.
            # We need to walk through and find ActionRows.
            if isinstance(child, Gtk.ListBox):
                row = child.get_first_child()
                while row:
                    next_row = row.get_next_sibling()
                    rows_to_remove.append(row)
                    row = next_row
            child = child.get_next_sibling()
        for row in rows_to_remove:
            group.remove(row)

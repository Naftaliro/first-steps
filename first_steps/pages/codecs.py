# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright 2026 Naftali Rosen
"""Codecs & Media page — install restricted extras, GStreamer, DVD support."""

import os
import subprocess

import gi

gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")

from gi.repository import Adw, GLib, Gtk

from first_steps.pages import BasePage


# Package groups the user can select
CODEC_GROUPS = {
    "restricted": {
        "title": "Ubuntu Restricted Extras",
        "subtitle": "Microsoft fonts, Flash fallback, MP3/AAC codecs, unrar",
        "packages": ["ubuntu-restricted-extras"],
        "default": True,
    },
    "gstreamer": {
        "title": "GStreamer Multimedia Plugins",
        "subtitle": "Full GStreamer codec pack (good, bad, ugly)",
        "packages": [
            "gstreamer1.0-plugins-good",
            "gstreamer1.0-plugins-bad",
            "gstreamer1.0-plugins-ugly",
            "gstreamer1.0-libav",
        ],
        "default": True,
    },
    "dvd": {
        "title": "DVD Playback Support",
        "subtitle": "libdvdcss2 via libdvd-pkg for encrypted DVD playback",
        "packages": ["libdvd-pkg"],
        "default": False,
    },
    "vaapi": {
        "title": "Hardware Video Acceleration",
        "subtitle": "VA-API support for Intel/AMD GPUs",
        "packages": ["gstreamer1.0-vaapi", "va-driver-all"],
        "default": False,
    },
}


class CodecsPage(BasePage):
    PAGE_TAG = "codecs"
    PAGE_TITLE = "Codecs & Media"

    def build_ui(self) -> None:
        self.add_status_page(
            "media-playback-start-symbolic",
            "Codecs & Media",
            "Install multimedia codecs so you can play any audio or video format. "
            "These are not included by default for licensing reasons."
        )

        self._checks: dict[str, Gtk.CheckButton] = {}

        group = self.add_preferences_group(
            "Available Codec Packs",
            "Select which codec packages to install:"
        )

        for key, info in CODEC_GROUPS.items():
            row, check = self.add_action_row_with_check(
                group,
                info["title"],
                info["subtitle"],
                active=info["default"],
            )
            self._checks[key] = check

        # Status / progress area
        self._status_group = self.add_preferences_group("Installation Status")
        self._status_label = Gtk.Label(label="Ready to install.")
        self._status_label.set_xalign(0)
        self._status_label.add_css_class("dim-label")
        self._status_label.set_wrap(True)
        self._status_group.add(
            self._wrap_in_row(self._status_label)
        )

        self._spinner = Gtk.Spinner()
        self._spinner.set_visible(False)

        # Install button
        btn_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=12)
        btn_box.set_halign(Gtk.Align.CENTER)
        btn_box.set_margin_top(8)

        self._install_btn = Gtk.Button(label="Install Selected Codecs")
        self._install_btn.add_css_class("suggested-action")
        self._install_btn.connect("clicked", self._on_install_clicked)
        btn_box.append(self._install_btn)
        btn_box.append(self._spinner)
        self._outer_box.append(btn_box)

        self.add_navigation_buttons(back_tag="welcome", next_tag="flatpak")

    def _wrap_in_row(self, widget: Gtk.Widget) -> Adw.ActionRow:
        """Wrap a widget in an ActionRow for use in a PreferencesGroup."""
        row = Adw.ActionRow()
        row.set_child(widget)
        return row

    def _on_install_clicked(self, btn: Gtk.Button) -> None:
        packages: list[str] = []
        selected_names: list[str] = []
        for key, check in self._checks.items():
            if check.get_active():
                packages.extend(CODEC_GROUPS[key]["packages"])
                selected_names.append(CODEC_GROUPS[key]["title"])

        if not packages:
            self._status_label.set_text("Nothing selected. Check at least one group.")
            return

        self._install_btn.set_sensitive(False)
        self._spinner.set_visible(True)
        self._spinner.start()
        self._status_label.set_text(f"Installing: {', '.join(selected_names)}...")

        # Write a helper script that sets DEBIAN_FRONTEND properly.
        # pkexec strips environment variables, so we must set it inside the script.
        script_path = "/tmp/first-steps-codecs.sh"
        script_lines = [
            "#!/bin/bash",
            "set -e",
            "export DEBIAN_FRONTEND=noninteractive",
            "apt-get update -qq",
            f"apt-get install -y {' '.join(packages)}",
        ]

        # If DVD was selected, run dpkg-reconfigure
        if self._checks["dvd"].get_active():
            script_lines.append(
                "dpkg-reconfigure -f noninteractive libdvd-pkg 2>/dev/null || true"
            )

        try:
            with open(script_path, "w") as f:
                f.write("\n".join(script_lines) + "\n")
            os.chmod(script_path, 0o755)
        except Exception as e:
            self._status_label.set_text(f"Error preparing install script: {e}")
            self._install_btn.set_sensitive(True)
            self._spinner.stop()
            self._spinner.set_visible(False)
            return

        self.run_privileged(
            ["bash", script_path],
            success_msg=f"Installed codecs: {', '.join(selected_names)}",
            callback=self._on_install_done,
        )

    def _on_install_done(self, success: bool, output: str) -> None:
        self._spinner.stop()
        self._spinner.set_visible(False)
        self._install_btn.set_sensitive(True)

        if success:
            self._status_label.set_text("All selected codecs installed successfully!")
            self._status_label.remove_css_class("dim-label")
            self.show_toast("Codecs installed successfully!")
        else:
            short_output = output.strip().split("\n")[-3:]  # Last 3 lines
            self._status_label.set_text(
                "Installation encountered an issue:\n" + "\n".join(short_output)
            )

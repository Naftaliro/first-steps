# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright 2026 Naftali Rosen
"""Privacy & Telemetry page — disable tracking, harden privacy settings."""

import os
import subprocess
import tempfile
import threading

import gi

gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")

from gi.repository import Adw, GLib, Gtk

from first_steps.pages import BasePage


class PrivacyPage(BasePage):
    PAGE_TAG = "privacy"
    PAGE_TITLE = "Privacy"
    PAGE_ICON = "security-medium-symbolic"

    def build_ui(self) -> None:
        self.add_status_page(
            "security-medium-symbolic",
            "Privacy & Telemetry",
            "Control what data your system shares. Disable telemetry, "
            "harden privacy settings, and take control of your data."
        )

        # ── Telemetry & reporting ────────────────────────────────────
        telemetry_group = self.add_preferences_group(
            "Telemetry & Crash Reporting",
            "Disable system data collection:"
        )

        self._telem_ubuntu, self._sw_ubuntu = self.add_action_row_with_switch(
            telemetry_group,
            "Disable Ubuntu Telemetry",
            "Remove ubuntu-report and apport crash reporting",
            active=True,
        )

        self._telem_whoopsie, self._sw_whoopsie = self.add_action_row_with_switch(
            telemetry_group,
            "Disable Whoopsie Error Reporting",
            "Stop automatic error report uploads to Canonical",
            active=True,
        )

        self._telem_popularity, self._sw_popularity = self.add_action_row_with_switch(
            telemetry_group,
            "Disable Popularity Contest",
            "Stop anonymous package usage statistics",
            active=True,
        )

        apply_telemetry_btn = Gtk.Button(label="Apply Telemetry Settings")
        apply_telemetry_btn.add_css_class("suggested-action")
        apply_telemetry_btn.set_halign(Gtk.Align.CENTER)
        apply_telemetry_btn.connect("clicked", self._on_apply_telemetry)
        self._outer_box.append(apply_telemetry_btn)

        # ── GNOME privacy settings ───────────────────────────────────
        gnome_group = self.add_preferences_group(
            "Desktop Privacy",
            "GNOME desktop privacy settings (no root required):"
        )

        self._gnome_recent, self._sw_recent = self.add_action_row_with_switch(
            gnome_group,
            "Disable Recent Files Tracking",
            "Stop GNOME from remembering recently opened files",
            active=False,
        )

        self._gnome_location, self._sw_location = self.add_action_row_with_switch(
            gnome_group,
            "Disable Location Services",
            "Turn off geolocation for all applications",
            active=True,
        )

        self._gnome_camera, self._sw_camera = self.add_action_row_with_switch(
            gnome_group,
            "Disable Camera by Default",
            "Block camera access for applications",
            active=False,
        )

        self._gnome_microphone, self._sw_microphone = self.add_action_row_with_switch(
            gnome_group,
            "Disable Microphone by Default",
            "Block microphone access for applications",
            active=False,
        )

        self._gnome_autotrash, self._sw_autotrash = self.add_action_row_with_switch(
            gnome_group,
            "Auto-delete Trash (30 days)",
            "Automatically empty trash after 30 days",
            active=True,
        )

        self._gnome_autotemp, self._sw_autotemp = self.add_action_row_with_switch(
            gnome_group,
            "Auto-delete Temp Files (30 days)",
            "Automatically remove temporary files after 30 days",
            active=True,
        )

        apply_gnome_btn = Gtk.Button(label="Apply Desktop Privacy Settings")
        apply_gnome_btn.add_css_class("suggested-action")
        apply_gnome_btn.set_halign(Gtk.Align.CENTER)
        apply_gnome_btn.connect("clicked", self._on_apply_gnome_privacy)
        self._outer_box.append(apply_gnome_btn)

        # ── Browser privacy ──────────────────────────────────────────
        browser_group = self.add_preferences_group(
            "Browser Privacy",
            "Recommended browser extensions (install manually):"
        )

        extensions = [
            ("uBlock Origin", "Efficient ad and tracker blocker",
             "https://addons.mozilla.org/firefox/addon/ublock-origin/"),
            ("Privacy Badger", "Automatically blocks invisible trackers",
             "https://addons.mozilla.org/firefox/addon/privacy-badger17/"),
            ("HTTPS Everywhere", "Force HTTPS on supported sites",
             "Built into most modern browsers"),
            ("Cookie AutoDelete", "Auto-delete cookies when tabs close",
             "https://addons.mozilla.org/firefox/addon/cookie-autodelete/"),
        ]

        for name, desc, url in extensions:
            row = Adw.ActionRow()
            row.set_title(name)
            row.set_subtitle(desc)
            row.add_prefix(
                Gtk.Image.new_from_icon_name("web-browser-symbolic")
            )

            if url.startswith("http"):
                link_btn = Gtk.Button()
                link_btn.set_icon_name("external-link-symbolic")
                link_btn.set_valign(Gtk.Align.CENTER)
                link_btn.add_css_class("flat")
                link_btn.set_tooltip_text(f"Open: {url}")

                def _make_open_cb(u):
                    def _cb(_btn):
                        try:
                            subprocess.Popen(
                                ["xdg-open", u],
                                stdout=subprocess.DEVNULL,
                                stderr=subprocess.DEVNULL,
                            )
                        except FileNotFoundError:
                            pass
                    return _cb

                link_btn.connect("clicked", _make_open_cb(url))
                row.add_suffix(link_btn)

            browser_group.add(row)

        self.add_navigation_buttons(back_tag="network", next_tag="development")

    def _on_apply_telemetry(self, btn) -> None:
        """Disable selected telemetry services."""
        actions = []

        script = "#!/bin/bash\nset -e\nexport DEBIAN_FRONTEND=noninteractive\n"

        if self._sw_ubuntu.get_active():
            script += (
                "apt-get remove -y ubuntu-report 2>/dev/null || true\n"
                "systemctl disable apport.service 2>/dev/null || true\n"
                "systemctl stop apport.service 2>/dev/null || true\n"
                "sed -i 's/enabled=1/enabled=0/' /etc/default/apport 2>/dev/null || true\n"
            )
            actions.append("Ubuntu telemetry")

        if self._sw_whoopsie.get_active():
            script += (
                "apt-get remove -y whoopsie 2>/dev/null || true\n"
                "systemctl disable whoopsie.service 2>/dev/null || true\n"
                "systemctl stop whoopsie.service 2>/dev/null || true\n"
            )
            actions.append("Whoopsie")

        if self._sw_popularity.get_active():
            script += (
                "apt-get remove -y popularity-contest 2>/dev/null || true\n"
            )
            actions.append("Popularity contest")

        if not actions:
            self.show_toast("No telemetry options selected")
            return

        with tempfile.NamedTemporaryFile(mode="w", suffix=".sh", delete=False) as f:
            f.write(script)
            tmp_path = f.name
        os.chmod(tmp_path, 0o755)

        def _done(success, output):
            try:
                os.unlink(tmp_path)
            except OSError:
                pass
            if success:
                self.show_toast(f"Disabled: {', '.join(actions)}")
            else:
                self.show_error_dialog("Telemetry Removal Failed", output[:500])

        self.run_privileged(
            [tmp_path],
            f"Disabled telemetry: {', '.join(actions)}",
            _done
        )

    def _on_apply_gnome_privacy(self, btn) -> None:
        """Apply GNOME privacy settings via gsettings (no root needed)."""
        changes = []

        def _gs(schema, key, value):
            try:
                subprocess.run(
                    ["gsettings", "set", schema, key, value],
                    capture_output=True, text=True, timeout=5
                )
            except Exception:
                pass

        if self._sw_recent.get_active():
            _gs("org.gnome.desktop.privacy", "remember-recent-files", "false")
            changes.append("Recent files tracking disabled")

        if self._sw_location.get_active():
            _gs("org.gnome.system.location", "enabled", "false")
            changes.append("Location services disabled")

        if self._sw_camera.get_active():
            _gs("org.gnome.desktop.privacy", "disable-camera", "true")
            changes.append("Camera disabled")

        if self._sw_microphone.get_active():
            _gs("org.gnome.desktop.privacy", "disable-microphone", "true")
            changes.append("Microphone disabled")

        if self._sw_autotrash.get_active():
            _gs("org.gnome.desktop.privacy", "remove-old-trash-files", "true")
            _gs("org.gnome.desktop.privacy", "old-files-age", "30")
            changes.append("Auto-delete trash (30 days)")

        if self._sw_autotemp.get_active():
            _gs("org.gnome.desktop.privacy", "remove-old-temp-files", "true")
            _gs("org.gnome.desktop.privacy", "old-files-age", "30")
            changes.append("Auto-delete temp files (30 days)")

        if changes:
            for c in changes:
                self.window.log_action(c)
            self.mark_completed()
            self.show_toast(f"Applied {len(changes)} privacy setting(s)")
        else:
            self.show_toast("No privacy settings selected")

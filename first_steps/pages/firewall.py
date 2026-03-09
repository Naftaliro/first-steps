# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright 2026 Naftali Rosen
"""Firewall page — enable and configure UFW with sensible defaults."""

import os
import subprocess
import tempfile

import gi

gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")

from gi.repository import Adw, GLib, Gtk

from first_steps.pages import BasePage


# Common services users might want to allow
COMMON_SERVICES = [
    ("ssh", "SSH (port 22)", "Allow incoming SSH connections", False),
    ("http", "HTTP (port 80)", "Allow incoming web traffic", False),
    ("https", "HTTPS (port 443)", "Allow incoming secure web traffic", False),
    ("1714:1764/tcp", "KDE Connect (TCP)", "Allow KDE Connect / GSConnect", False),
    ("1714:1764/udp", "KDE Connect (UDP)", "Allow KDE Connect / GSConnect", False),
    ("5353/udp", "mDNS / Avahi", "Local network service discovery", True),
    ("631/tcp", "CUPS Printing", "Allow network printing", False),
    ("51413/tcp", "Transmission", "BitTorrent client", False),
]


class FirewallPage(BasePage):
    PAGE_TAG = "firewall"
    PAGE_TITLE = "Firewall"

    def build_ui(self) -> None:
        self.add_status_page(
            "security-high-symbolic",
            "Firewall",
            "UFW (Uncomplicated Firewall) protects your system from "
            "unauthorized network access. We'll enable it with a deny-incoming "
            "default and let you allow specific services."
        )

        # ── Status ───────────────────────────────────────────────────
        self._status_group = self.add_preferences_group("Firewall Status")

        self._status_row = Adw.ActionRow()
        self._status_row.set_title("UFW Firewall")
        self._status_row.set_subtitle("Checking...")
        self._status_group.add(self._status_row)

        GLib.idle_add(self._check_ufw_status)

        # ── Default policy ───────────────────────────────────────────
        self._policy_group = self.add_preferences_group(
            "Default Policy",
            "The default policy determines what happens to traffic that "
            "doesn't match any rule."
        )

        self._deny_incoming_row, self._deny_incoming_switch = self.add_action_row_with_switch(
            self._policy_group,
            "Deny Incoming Connections",
            "Block all incoming traffic unless explicitly allowed (recommended)",
            active=True,
        )

        self._allow_outgoing_row, self._allow_outgoing_switch = self.add_action_row_with_switch(
            self._policy_group,
            "Allow Outgoing Connections",
            "Allow all outgoing traffic (recommended)",
            active=True,
        )

        # ── Service exceptions ───────────────────────────────────────
        self._services_group = self.add_preferences_group(
            "Allow Services",
            "Select services to allow through the firewall:"
        )

        self._service_checks: dict[str, Gtk.CheckButton] = {}
        for port, name, desc, default in COMMON_SERVICES:
            row, check = self.add_action_row_with_check(
                self._services_group, name, desc, active=default
            )
            self._service_checks[port] = check

        # ── Apply ────────────────────────────────────────────────────
        btn_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=12)
        btn_box.set_halign(Gtk.Align.CENTER)
        btn_box.set_margin_top(8)

        self._apply_btn = Gtk.Button(label="Enable & Configure Firewall")
        self._apply_btn.add_css_class("suggested-action")
        self._apply_btn.connect("clicked", self._on_apply)
        btn_box.append(self._apply_btn)

        self._spinner = Gtk.Spinner()
        self._spinner.set_visible(False)
        btn_box.append(self._spinner)
        self._outer_box.append(btn_box)

        self._progress_label = Gtk.Label()
        self._progress_label.set_xalign(0)
        self._progress_label.set_wrap(True)
        self._progress_label.add_css_class("dim-label")
        self._progress_label.set_visible(False)
        self._outer_box.append(self._progress_label)

        self.add_navigation_buttons(back_tag="power", next_tag="extras")

    def _check_ufw_status(self) -> None:
        """Check UFW status — ufw status may need root, so try both ways."""
        try:
            # First try without root (works on some systems)
            result = subprocess.run(
                ["ufw", "status"],
                capture_output=True, text=True, timeout=5,
            )
            output = result.stdout.strip() + result.stderr.strip()

            if "Status: active" in output:
                self._status_row.set_subtitle("UFW is active and running")
                self._status_row.add_prefix(
                    Gtk.Image.new_from_icon_name("security-high-symbolic")
                )
                self._apply_btn.set_label("Reconfigure Firewall")
            elif "Status: inactive" in output:
                self._status_row.set_subtitle("UFW is installed but inactive")
                self._status_row.add_prefix(
                    Gtk.Image.new_from_icon_name("security-low-symbolic")
                )
            elif "command not found" in output.lower() or result.returncode == 127:
                self._status_row.set_subtitle("UFW is not installed \u2014 it will be installed")
                self._status_row.add_prefix(
                    Gtk.Image.new_from_icon_name("dialog-information-symbolic")
                )
            else:
                # Might need root; check if binary exists at least
                which = subprocess.run(
                    ["which", "ufw"], capture_output=True, text=True, timeout=5
                )
                if which.returncode == 0:
                    self._status_row.set_subtitle(
                        "UFW is installed (run status check requires authentication)"
                    )
                    self._status_row.add_prefix(
                        Gtk.Image.new_from_icon_name("dialog-information-symbolic")
                    )
                else:
                    self._status_row.set_subtitle("UFW is not installed \u2014 it will be installed")
                    self._status_row.add_prefix(
                        Gtk.Image.new_from_icon_name("dialog-information-symbolic")
                    )
        except FileNotFoundError:
            self._status_row.set_subtitle("UFW is not installed \u2014 it will be installed")
            self._status_row.add_prefix(
                Gtk.Image.new_from_icon_name("dialog-information-symbolic")
            )
        except Exception:
            self._status_row.set_subtitle("Could not check firewall status")

    def _on_apply(self, btn: Gtk.Button) -> None:
        btn.set_sensitive(False)
        self._spinner.set_visible(True)
        self._spinner.start()
        self._progress_label.set_text("Configuring firewall...")
        self._progress_label.set_visible(True)

        # Build configuration script
        incoming = "deny" if self._deny_incoming_switch.get_active() else "allow"
        outgoing = "allow" if self._allow_outgoing_switch.get_active() else "deny"

        allowed_ports = [
            port for port, check in self._service_checks.items()
            if check.get_active()
        ]

        script_lines = [
            "#!/bin/bash",
            "set -e",
            "",
            "# Install UFW if needed",
            "command -v ufw >/dev/null 2>&1 || apt-get install -y ufw",
            "",
            "# Reset to clean state",
            "ufw --force reset",
            "",
            f"# Set default policies",
            f"ufw default {incoming} incoming",
            f"ufw default {outgoing} outgoing",
            "",
        ]

        for port in allowed_ports:
            script_lines.append(f"ufw allow {port}")

        script_lines.extend([
            "",
            "# Enable the firewall",
            "ufw --force enable",
            "",
            "echo 'Firewall configured successfully'",
        ])

        # Use tempfile.mkstemp to avoid TOCTOU race conditions.
        try:
            fd, tmp_script = tempfile.mkstemp(
                prefix="first-steps-", suffix=".sh", dir="/tmp"
            )
            with os.fdopen(fd, "w") as f:
                f.write("\n".join(script_lines) + "\n")
            os.chmod(tmp_script, 0o755)
        except Exception as e:
            self._progress_label.set_text(f"Error: {e}")
            btn.set_sensitive(True)
            self._spinner.stop()
            self._spinner.set_visible(False)
            return

        allowed_names = []
        for port, name, _, _ in COMMON_SERVICES:
            if port in allowed_ports:
                allowed_names.append(name)

        desc = f"Enabled UFW firewall (default {incoming} incoming)"
        if allowed_names:
            desc += f", allowed: {', '.join(allowed_names)}"

        self.run_privileged(
            ["bash", tmp_script],
            success_msg=desc,
            callback=self._on_apply_done,
        )

    def _on_apply_done(self, success: bool, output: str) -> None:
        self._spinner.stop()
        self._spinner.set_visible(False)
        self._apply_btn.set_sensitive(True)

        if success:
            self._progress_label.set_text("Firewall is now active and configured!")
            self._status_row.set_subtitle("UFW is active and running")
            self.show_toast("Firewall enabled!")
        else:
            short = output.strip().split("\n")[-3:]
            self._progress_label.set_text(
                "Firewall configuration encountered an issue:\n" + "\n".join(short)
            )

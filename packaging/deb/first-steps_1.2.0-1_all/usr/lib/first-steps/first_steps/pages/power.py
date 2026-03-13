# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright 2026 Naftali
"""Power & Performance page — power profiles, lid behavior, suspend timeout."""

import os
import subprocess
import tempfile

import gi

gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")

from gi.repository import Adw, GLib, Gtk

from first_steps.pages import BasePage


POWER_PROFILES = [
    ("power-saver", "Power Saver", "Maximize battery life, reduce performance"),
    ("balanced", "Balanced", "Good mix of performance and battery life (recommended)"),
    ("performance", "Performance", "Maximum performance, higher power consumption"),
]

LID_ACTIONS = [
    ("suspend", "Suspend", "Put the computer to sleep (recommended)"),
    ("hibernate", "Hibernate", "Save state to disk and power off"),
    ("lock", "Lock Screen", "Lock the screen but stay awake"),
    ("ignore", "Do Nothing", "Keep running with the lid closed"),
]

SUSPEND_TIMEOUTS = [
    (0, "Never"),
    (300, "5 minutes"),
    (600, "10 minutes"),
    (900, "15 minutes"),
    (1200, "20 minutes"),
    (1800, "30 minutes"),
    (3600, "1 hour"),
]


class PowerPage(BasePage):
    PAGE_TAG = "power"
    PAGE_TITLE = "Power"

    def build_ui(self) -> None:
        self.add_status_page(
            "battery-symbolic",
            "Power & Performance",
            "Configure how your system manages power. These settings affect "
            "performance, battery life, and sleep behavior."
        )

        # ── Power Profile ────────────────────────────────────────────
        self._profile_group = self.add_preferences_group(
            "Power Profile",
            "Set the default power management profile:"
        )

        self._profile_model = Gtk.StringList.new(
            [f"{name} \u2014 {desc}" for _, name, desc in POWER_PROFILES]
        )
        self._profile_row = Adw.ComboRow()
        self._profile_row.set_title("Active Profile")
        self._profile_row.set_model(self._profile_model)
        self._profile_row.set_selected(1)  # Default to balanced
        self._profile_group.add(self._profile_row)

        # Detect current profile
        GLib.idle_add(self._detect_current_profile)

        # ── Lid Behavior ─────────────────────────────────────────────
        self._lid_group = self.add_preferences_group(
            "Lid Close Behavior",
            "What happens when you close your laptop lid:"
        )

        self._lid_ac_model = Gtk.StringList.new(
            [name for _, name, _ in LID_ACTIONS]
        )
        self._lid_ac_row = Adw.ComboRow()
        self._lid_ac_row.set_title("On AC Power")
        self._lid_ac_row.set_subtitle("Action when lid is closed while plugged in")
        self._lid_ac_row.set_model(self._lid_ac_model)
        self._lid_ac_row.set_selected(0)  # suspend
        self._lid_group.add(self._lid_ac_row)

        self._lid_bat_model = Gtk.StringList.new(
            [name for _, name, _ in LID_ACTIONS]
        )
        self._lid_bat_row = Adw.ComboRow()
        self._lid_bat_row.set_title("On Battery")
        self._lid_bat_row.set_subtitle("Action when lid is closed on battery power")
        self._lid_bat_row.set_model(self._lid_bat_model)
        self._lid_bat_row.set_selected(0)  # suspend
        self._lid_group.add(self._lid_bat_row)

        # ── Suspend Timeout ──────────────────────────────────────────
        self._suspend_group = self.add_preferences_group(
            "Auto-Suspend",
            "Automatically suspend after a period of inactivity:"
        )

        self._suspend_ac_model = Gtk.StringList.new(
            [label for _, label in SUSPEND_TIMEOUTS]
        )
        self._suspend_ac_row = Adw.ComboRow()
        self._suspend_ac_row.set_title("On AC Power")
        self._suspend_ac_row.set_model(self._suspend_ac_model)
        self._suspend_ac_row.set_selected(0)  # Never
        self._suspend_group.add(self._suspend_ac_row)

        self._suspend_bat_model = Gtk.StringList.new(
            [label for _, label in SUSPEND_TIMEOUTS]
        )
        self._suspend_bat_row = Adw.ComboRow()
        self._suspend_bat_row.set_title("On Battery")
        self._suspend_bat_row.set_model(self._suspend_bat_model)
        self._suspend_bat_row.set_selected(3)  # 15 minutes
        self._suspend_group.add(self._suspend_bat_row)

        # ── Screen Blank ─────────────────────────────────────────────
        self._screen_group = self.add_preferences_group("Screen")

        self._dim_row, self._dim_switch = self.add_action_row_with_switch(
            self._screen_group,
            "Dim Screen When Inactive",
            "Reduce brightness before turning off the screen",
            active=True,
        )

        # ── Apply button ─────────────────────────────────────────────
        btn_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=12)
        btn_box.set_halign(Gtk.Align.CENTER)
        btn_box.set_margin_top(8)

        self._apply_btn = Gtk.Button(label="Apply Settings")
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

        self.add_navigation_buttons(back_tag="timeshift", next_tag="firewall")

    def _detect_current_profile(self) -> None:
        """Detect the currently active power profile."""
        try:
            result = subprocess.run(
                ["powerprofilesctl", "get"],
                capture_output=True, text=True, timeout=5,
            )
            if result.returncode == 0:
                current = result.stdout.strip()
                for i, (key, _, _) in enumerate(POWER_PROFILES):
                    if key == current:
                        self._profile_row.set_selected(i)
                        break
        except (FileNotFoundError, Exception):
            pass  # powerprofilesctl may not be available

    def _on_apply(self, btn: Gtk.Button) -> None:
        btn.set_sensitive(False)
        self._spinner.set_visible(True)
        self._spinner.start()
        self._progress_label.set_text("Applying power settings...")
        self._progress_label.set_visible(True)

        # 1. Power profile
        profile_idx = self._profile_row.get_selected()
        profile_key = POWER_PROFILES[profile_idx][0]
        profile_name = POWER_PROFILES[profile_idx][1]

        # 2. Lid actions
        lid_ac_idx = self._lid_ac_row.get_selected()
        lid_ac_key = LID_ACTIONS[lid_ac_idx][0]
        lid_bat_idx = self._lid_bat_row.get_selected()
        lid_bat_key = LID_ACTIONS[lid_bat_idx][0]

        # 3. Suspend timeouts
        suspend_ac_idx = self._suspend_ac_row.get_selected()
        suspend_ac_val = SUSPEND_TIMEOUTS[suspend_ac_idx][0]
        suspend_bat_idx = self._suspend_bat_row.get_selected()
        suspend_bat_val = SUSPEND_TIMEOUTS[suspend_bat_idx][0]

        # Build a script that applies privileged settings
        script_lines = [
            "#!/bin/bash",
            "set -e",
            "",
            f"# Set power profile",
            f"powerprofilesctl set {profile_key} 2>/dev/null || true",
            "",
            "# Configure lid close behavior via logind.conf",
            "mkdir -p /etc/systemd/logind.conf.d",
            "cat > /etc/systemd/logind.conf.d/first-steps-lid.conf << 'EOF'",
            "[Login]",
            f"HandleLidSwitch={lid_bat_key}",
            f"HandleLidSwitchExternalPower={lid_ac_key}",
            f"HandleLidSwitchDocked={lid_ac_key}",
            "EOF",
            "",
            "# Restart logind to apply lid settings",
            "systemctl kill -s HUP systemd-logind 2>/dev/null || true",
        ]

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

        self.run_privileged(
            ["bash", tmp_script],
            success_msg=f"Configured power profile: {profile_name}, lid behavior, suspend timeouts",
            callback=lambda s, o: self._on_privileged_done(
                s, o, suspend_ac_val, suspend_bat_val
            ),
        )

    def _on_privileged_done(
        self, success: bool, output: str,
        suspend_ac: int, suspend_bat: int
    ) -> None:
        # Apply GSettings for suspend (runs as current user, no elevation)
        if success:
            try:
                subprocess.run([
                    "gsettings", "set",
                    "org.gnome.settings-daemon.plugins.power",
                    "sleep-inactive-ac-timeout",
                    str(suspend_ac),
                ], timeout=5, capture_output=True)
                subprocess.run([
                    "gsettings", "set",
                    "org.gnome.settings-daemon.plugins.power",
                    "sleep-inactive-battery-timeout",
                    str(suspend_bat),
                ], timeout=5, capture_output=True)

                dim = self._dim_switch.get_active()
                subprocess.run([
                    "gsettings", "set",
                    "org.gnome.settings-daemon.plugins.power",
                    "idle-dim",
                    "true" if dim else "false",
                ], timeout=5, capture_output=True)
            except Exception:
                pass

        self._spinner.stop()
        self._spinner.set_visible(False)
        self._apply_btn.set_sensitive(True)

        if success:
            self._progress_label.set_text("Power settings applied successfully!")
            self.show_toast("Power settings applied!")
        else:
            short = output.strip().split("\n")[-3:]
            self._progress_label.set_text(
                "Some settings may not have been applied:\n" + "\n".join(short)
            )

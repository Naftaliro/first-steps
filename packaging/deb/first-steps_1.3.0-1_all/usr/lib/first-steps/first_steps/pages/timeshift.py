# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright 2026 Naftali Rosen
"""Timeshift page — configure automatic system backups with sane defaults."""

import json
import os
import subprocess
import tempfile

import gi

gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")

from gi.repository import Adw, GLib, Gtk

from first_steps.pages import BasePage


# Sane defaults for Timeshift configuration
DEFAULT_TIMESHIFT_CONFIG = {
    "backup_device_uuid": "",
    "parent_device_uuid": "",
    "do_first_run": True,
    "btrfs_mode": False,
    "include_btrfs_home_for_backup": False,
    "include_btrfs_home_for_restore": False,
    "stop_cron_emails": True,
    "schedule_monthly": False,
    "schedule_weekly": True,
    "schedule_daily": False,
    "schedule_hourly": False,
    "schedule_boot": False,
    "count_monthly": 2,
    "count_weekly": 3,
    "count_daily": 5,
    "count_hourly": 6,
    "count_boot": 5,
    "snapshot_size": 0,
    "snapshot_count": 0,
    "date_format": "%Y-%m-%d %H:%M:%S",
    "exclude": ["/root/**"],
    "exclude-apps": [],
}


class TimeshiftPage(BasePage):
    PAGE_TAG = "timeshift"
    PAGE_TITLE = "Backup"

    def build_ui(self) -> None:
        self.add_status_page(
            "drive-harddisk-symbolic",
            "Backup Setup",
            "Timeshift creates system snapshots that let you roll back if "
            "something goes wrong. We'll set it up with sensible defaults \u2014 "
            "weekly snapshots, keeping the last 3."
        )

        # ── Status ───────────────────────────────────────────────────
        self._status_group = self.add_preferences_group("Timeshift Status")

        self._status_row = Adw.ActionRow()
        self._status_row.set_title("Timeshift")
        self._status_row.set_subtitle("Checking...")
        self._status_group.add(self._status_row)

        GLib.idle_add(self._check_timeshift_status)

        # ── Schedule config ──────────────────────────────────────────
        self._schedule_group = self.add_preferences_group(
            "Snapshot Schedule",
            "Choose how often to create automatic snapshots:"
        )

        self._weekly_row, self._weekly_switch = self.add_action_row_with_switch(
            self._schedule_group,
            "Weekly Snapshots",
            "Create a snapshot every week (recommended)",
            active=True,
        )

        self._daily_row, self._daily_switch = self.add_action_row_with_switch(
            self._schedule_group,
            "Daily Snapshots",
            "Create a snapshot every day",
            active=False,
        )

        self._boot_row, self._boot_switch = self.add_action_row_with_switch(
            self._schedule_group,
            "Boot Snapshots",
            "Create a snapshot on each boot",
            active=False,
        )

        # ── Retention ────────────────────────────────────────────────
        self._retention_group = self.add_preferences_group(
            "Retention Policy",
            "How many snapshots to keep for each schedule:"
        )

        self._weekly_count_row = Adw.SpinRow.new_with_range(1, 10, 1)
        self._weekly_count_row.set_title("Weekly snapshots to keep")
        self._weekly_count_row.set_value(3)
        self._retention_group.add(self._weekly_count_row)

        self._daily_count_row = Adw.SpinRow.new_with_range(1, 14, 1)
        self._daily_count_row.set_title("Daily snapshots to keep")
        self._daily_count_row.set_value(5)
        self._retention_group.add(self._daily_count_row)

        self._boot_count_row = Adw.SpinRow.new_with_range(1, 10, 1)
        self._boot_count_row.set_title("Boot snapshots to keep")
        self._boot_count_row.set_value(3)
        self._retention_group.add(self._boot_count_row)

        # ── Options ──────────────────────────────────────────────────
        self._options_group = self.add_preferences_group("Options")

        self._exclude_home_row, self._exclude_home_switch = self.add_action_row_with_switch(
            self._options_group,
            "Exclude /home from snapshots",
            "Recommended \u2014 your personal files are not affected by system rollbacks",
            active=True,
        )

        # ── Action buttons ───────────────────────────────────────────
        btn_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=12)
        btn_box.set_halign(Gtk.Align.CENTER)
        btn_box.set_margin_top(8)

        self._install_btn = Gtk.Button(label="Install & Configure Timeshift")
        self._install_btn.add_css_class("suggested-action")
        self._install_btn.connect("clicked", self._on_setup)
        btn_box.append(self._install_btn)

        self._spinner = Gtk.Spinner()
        self._spinner.set_visible(False)
        btn_box.append(self._spinner)
        self._outer_box.append(btn_box)

        self._snapshot_btn = Gtk.Button(label="Create First Snapshot Now")
        self._snapshot_btn.set_halign(Gtk.Align.CENTER)
        self._snapshot_btn.set_margin_top(4)
        self._snapshot_btn.connect("clicked", self._on_create_snapshot)
        self._snapshot_btn.set_visible(False)
        self._outer_box.append(self._snapshot_btn)

        # Progress
        self._progress_label = Gtk.Label()
        self._progress_label.set_xalign(0)
        self._progress_label.set_wrap(True)
        self._progress_label.add_css_class("dim-label")
        self._progress_label.set_visible(False)
        self._outer_box.append(self._progress_label)

        self.add_navigation_buttons(back_tag="bottles", next_tag="power")

    def _check_timeshift_status(self) -> None:
        try:
            result = subprocess.run(
                ["which", "timeshift"],
                capture_output=True, text=True, timeout=5,
            )
            if result.returncode == 0:
                self._status_row.set_subtitle("Timeshift is installed")
                self._status_row.add_prefix(
                    Gtk.Image.new_from_icon_name("emblem-ok-symbolic")
                )
                self._install_btn.set_label("Reconfigure Timeshift")
            else:
                self._status_row.set_subtitle("Timeshift is not installed")
                self._status_row.add_prefix(
                    Gtk.Image.new_from_icon_name("dialog-information-symbolic")
                )
        except Exception:
            self._status_row.set_subtitle("Could not check Timeshift status")

    def _on_setup(self, btn: Gtk.Button) -> None:
        btn.set_sensitive(False)
        self._spinner.set_visible(True)
        self._spinner.start()
        self._progress_label.set_text("Installing and configuring Timeshift...")
        self._progress_label.set_visible(True)

        # Build config from UI selections
        config = DEFAULT_TIMESHIFT_CONFIG.copy()
        config["schedule_weekly"] = self._weekly_switch.get_active()
        config["schedule_daily"] = self._daily_switch.get_active()
        config["schedule_boot"] = self._boot_switch.get_active()
        config["count_weekly"] = int(self._weekly_count_row.get_value())
        config["count_daily"] = int(self._daily_count_row.get_value())
        config["count_boot"] = int(self._boot_count_row.get_value())

        if self._exclude_home_switch.get_active():
            config["exclude"] = ["/root/**", "/home/**"]
        else:
            config["exclude"] = ["/root/**"]

        # Write config to temp file.
        # Use tempfile.mkstemp to avoid TOCTOU race conditions.
        try:
            fd_cfg, tmp_config = tempfile.mkstemp(
                prefix="first-steps-", suffix=".json", dir="/tmp"
            )
            with os.fdopen(fd_cfg, "w") as f:
                json.dump(config, f, indent=2)
        except Exception as e:
            self._progress_label.set_text(f"Error writing config: {e}")
            self._spinner.stop()
            self._spinner.set_visible(False)
            btn.set_sensitive(True)
            return

        # Single privileged script: install + configure in one pkexec prompt.
        # Use tempfile.mkstemp to avoid TOCTOU race conditions.
        script_lines = [
            "#!/bin/bash",
            "set -e",
            "export DEBIAN_FRONTEND=noninteractive",
            "",
            "# Install Timeshift if not present",
            "command -v timeshift >/dev/null 2>&1 || apt-get install -y timeshift",
            "",
            "# Write configuration",
            "mkdir -p /etc/timeshift",
            f"cp {tmp_config} /etc/timeshift/timeshift.json",
            "",
            "echo 'Timeshift configured successfully'",
        ]
        try:
            fd_sh, script_path = tempfile.mkstemp(
                prefix="first-steps-", suffix=".sh", dir="/tmp"
            )
            with os.fdopen(fd_sh, "w") as f:
                f.write("\n".join(script_lines) + "\n")
            os.chmod(script_path, 0o755)
        except Exception as e:
            self._progress_label.set_text(f"Error: {e}")
            self._spinner.stop()
            self._spinner.set_visible(False)
            btn.set_sensitive(True)
            return

        self.run_privileged(
            ["bash", script_path],
            success_msg="Installed and configured Timeshift (weekly snapshots, keep 3)",
            callback=self._on_setup_done,
        )

    def _on_setup_done(self, success: bool, output: str) -> None:
        self._spinner.stop()
        self._spinner.set_visible(False)
        self._install_btn.set_sensitive(True)

        if success:
            self._progress_label.set_text(
                "Timeshift is installed and configured! "
                "Automatic snapshots will run on schedule."
            )
            self._snapshot_btn.set_visible(True)
            self._status_row.set_subtitle("Timeshift is installed and configured")
            self.show_toast("Timeshift configured!")
        else:
            short = output.strip().split("\n")[-3:]
            self._progress_label.set_text(
                "Setup encountered an issue:\n" + "\n".join(short)
            )

    def _on_create_snapshot(self, btn: Gtk.Button) -> None:
        btn.set_sensitive(False)
        self._progress_label.set_text("Creating first snapshot... This may take a few minutes.")

        self.run_privileged(
            ["timeshift", "--create", "--comments",
             "First Steps initial snapshot"],
            success_msg="Created initial Timeshift snapshot",
            callback=self._on_snapshot_done,
        )

    def _on_snapshot_done(self, success: bool, output: str) -> None:
        self._snapshot_btn.set_sensitive(True)
        if success:
            self._progress_label.set_text("First snapshot created successfully!")
            self.show_toast("First snapshot created!")
        else:
            short = output.strip().split("\n")[-3:]
            self._progress_label.set_text(
                "Snapshot creation encountered an issue:\n" + "\n".join(short)
            )

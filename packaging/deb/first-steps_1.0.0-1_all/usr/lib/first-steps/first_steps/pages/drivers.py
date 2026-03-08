# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright 2026 First Steps Contributors
"""Drivers page — detect hardware and install recommended drivers."""

import gi
import subprocess
import re

gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")

from gi.repository import Adw, GLib, Gtk

from first_steps.pages import BasePage


class DriversPage(BasePage):
    PAGE_TAG = "drivers"
    PAGE_TITLE = "Drivers"

    def build_ui(self) -> None:
        self.add_status_page(
            "preferences-system-symbolic",
            "Driver Detection",
            "Scan your hardware and install the best available drivers. "
            "This wraps ubuntu-drivers so you never need to touch a terminal."
        )

        # Scan button
        self._scan_btn = Gtk.Button(label="Scan for Drivers")
        self._scan_btn.add_css_class("suggested-action")
        self._scan_btn.set_halign(Gtk.Align.CENTER)
        self._scan_btn.connect("clicked", self._on_scan)
        self._outer_box.append(self._scan_btn)

        self._spinner = Gtk.Spinner()
        self._spinner.set_halign(Gtk.Align.CENTER)
        self._spinner.set_visible(False)
        self._outer_box.append(self._spinner)

        # Results group (populated after scan)
        self._results_group = self.add_preferences_group(
            "Detected Drivers",
            "No scan performed yet."
        )

        self._driver_checks: dict[str, Gtk.CheckButton] = {}

        # Install button (hidden until scan)
        btn_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=12)
        btn_box.set_halign(Gtk.Align.CENTER)
        btn_box.set_margin_top(8)

        self._install_btn = Gtk.Button(label="Install Selected Drivers")
        self._install_btn.add_css_class("suggested-action")
        self._install_btn.set_visible(False)
        self._install_btn.connect("clicked", self._on_install)
        btn_box.append(self._install_btn)

        self._install_spinner = Gtk.Spinner()
        self._install_spinner.set_visible(False)
        btn_box.append(self._install_spinner)
        self._outer_box.append(btn_box)

        # Status
        self._status_label = Gtk.Label()
        self._status_label.set_xalign(0)
        self._status_label.set_wrap(True)
        self._status_label.add_css_class("dim-label")
        self._status_label.set_visible(False)
        self._outer_box.append(self._status_label)

        self.add_navigation_buttons(back_tag="flatpak", next_tag="bottles")

    def _on_scan(self, btn: Gtk.Button) -> None:
        btn.set_sensitive(False)
        self._spinner.set_visible(True)
        self._spinner.start()
        self._results_group.set_description("Scanning hardware...")

        self.run_unprivileged(
            ["ubuntu-drivers", "devices"],
            success_msg="",  # Don't log scan as an action
            callback=self._on_scan_done,
        )

    def _on_scan_done(self, success: bool, output: str) -> None:
        self._spinner.stop()
        self._spinner.set_visible(False)
        self._scan_btn.set_sensitive(True)

        # Clear previous results
        while True:
            child = self._results_group.get_first_child()
            # Skip the group's internal header children
            if child is None:
                break
            # Only remove ActionRow children we added
            if isinstance(child, Adw.ActionRow):
                self._results_group.remove(child)
            else:
                break

        self._driver_checks.clear()

        if not success or not output.strip():
            self._results_group.set_description(
                "No drivers detected, or ubuntu-drivers is not available.\n"
                "Your system may already have the best drivers installed."
            )
            return

        # Parse ubuntu-drivers devices output
        drivers = self._parse_drivers(output)

        if not drivers:
            self._results_group.set_description(
                "No additional drivers are available. Your system is using "
                "the best drivers already."
            )
            return

        self._results_group.set_description(
            f"Found {len(drivers)} available driver(s):"
        )

        for drv in drivers:
            is_recommended = drv.get("recommended", False)
            title = drv["package"]
            subtitle_parts = []
            if drv.get("vendor"):
                subtitle_parts.append(drv["vendor"])
            if drv.get("device"):
                subtitle_parts.append(drv["device"])
            if is_recommended:
                subtitle_parts.append("★ Recommended")
            subtitle = " — ".join(subtitle_parts)

            row, check = self.add_action_row_with_check(
                self._results_group,
                title,
                subtitle,
                active=is_recommended,
            )
            self._driver_checks[drv["package"]] = check

        self._install_btn.set_visible(True)

    @staticmethod
    def _parse_drivers(output: str) -> list[dict]:
        """Parse the output of `ubuntu-drivers devices`."""
        drivers = []
        current_device = {}

        for line in output.splitlines():
            line = line.strip()
            if line.startswith("=="):
                if current_device:
                    current_device = {}
                continue

            if line.startswith("vendor"):
                current_device["vendor"] = line.split(":", 1)[-1].strip()
            elif line.startswith("model"):
                current_device["device"] = line.split(":", 1)[-1].strip()
            elif line.startswith("driver"):
                # e.g. "driver   : nvidia-driver-535 - distro non-free recommended"
                match = re.match(
                    r"driver\s*:\s*(\S+)\s*-\s*(.*)", line
                )
                if match:
                    pkg = match.group(1)
                    info = match.group(2)
                    recommended = "recommended" in info.lower()
                    drivers.append({
                        "package": pkg,
                        "vendor": current_device.get("vendor", ""),
                        "device": current_device.get("device", ""),
                        "recommended": recommended,
                        "info": info.strip(),
                    })

        return drivers

    def _on_install(self, btn: Gtk.Button) -> None:
        selected = [
            pkg for pkg, check in self._driver_checks.items()
            if check.get_active()
        ]
        if not selected:
            self._status_label.set_text("No drivers selected.")
            self._status_label.set_visible(True)
            return

        btn.set_sensitive(False)
        self._install_spinner.set_visible(True)
        self._install_spinner.start()
        self._status_label.set_text(f"Installing: {', '.join(selected)}...")
        self._status_label.set_visible(True)

        cmd = ["apt-get", "install", "-y"] + selected

        self.run_privileged(
            cmd,
            success_msg=f"Installed drivers: {', '.join(selected)}",
            callback=self._on_install_done,
        )

    def _on_install_done(self, success: bool, output: str) -> None:
        self._install_spinner.stop()
        self._install_spinner.set_visible(False)
        self._install_btn.set_sensitive(True)

        if success:
            self._status_label.set_text(
                "Drivers installed successfully! A reboot may be required "
                "for changes to take effect."
            )
        else:
            self._status_label.set_text(
                f"Driver installation encountered an issue.\n{output[:300]}"
            )

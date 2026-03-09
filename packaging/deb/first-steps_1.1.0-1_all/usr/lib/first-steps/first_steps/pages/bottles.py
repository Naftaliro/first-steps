# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright 2026 Naftali
"""Bottles page — install and pre-configure Bottles for Windows app compatibility."""

import os
import subprocess
import tempfile

import gi

gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")

from gi.repository import Adw, GLib, Gtk

from first_steps.pages import BasePage


class BottlesPage(BasePage):
    PAGE_TAG = "bottles"
    PAGE_TITLE = "Windows Apps"

    def build_ui(self) -> None:
        self.add_status_page(
            "preferences-desktop-apps-symbolic",
            "Windows App Compatibility",
            "Bottles is a modern Wine frontend that lets you run Windows "
            "applications and games in isolated environments called 'bottles'.\n\n"
            "We'll install Bottles via Flatpak and help you create your first bottle."
        )

        # ── Status check ─────────────────────────────────────────────
        self._status_group = self.add_preferences_group("Bottles Status")

        self._status_row = Adw.ActionRow()
        self._status_row.set_title("Bottles")
        self._status_row.set_subtitle("Checking installation status...")
        self._status_group.add(self._status_row)

        GLib.idle_add(self._check_bottles_status)

        # ── Install section ──────────────────────────────────────────
        self._install_group = self.add_preferences_group(
            "Install Bottles",
            "Bottles will be installed from Flathub as a Flatpak application."
        )

        # Wine dependencies option
        self._wine_row, self._wine_check = self.add_action_row_with_check(
            self._install_group,
            "Install Wine Dependencies",
            "Recommended system libraries for best compatibility",
            active=True,
        )

        self._gamemode_row, self._gamemode_check = self.add_action_row_with_check(
            self._install_group,
            "Install GameMode",
            "Feral Interactive's GameMode for better gaming performance",
            active=False,
        )

        btn_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=12)
        btn_box.set_halign(Gtk.Align.CENTER)
        btn_box.set_margin_top(8)

        self._install_btn = Gtk.Button(label="Install Bottles")
        self._install_btn.add_css_class("suggested-action")
        self._install_btn.connect("clicked", self._on_install)
        btn_box.append(self._install_btn)

        self._spinner = Gtk.Spinner()
        self._spinner.set_visible(False)
        btn_box.append(self._spinner)
        self._outer_box.append(btn_box)

        # ── First Bottle Setup ───────────────────────────────────────
        self._bottle_group = self.add_preferences_group(
            "Create Your First Bottle",
            "A 'bottle' is an isolated Windows environment. Choose a template:"
        )

        self._bottle_type = Gtk.StringList.new([
            "Gaming \u2014 Optimized for games (DXVK, VKD3D, GameMode)",
            "Application \u2014 For productivity software",
            "Custom \u2014 Minimal, configure yourself",
        ])

        self._bottle_dropdown_row = Adw.ComboRow()
        self._bottle_dropdown_row.set_title("Bottle Template")
        self._bottle_dropdown_row.set_subtitle("Select the type of environment to create")
        self._bottle_dropdown_row.set_model(self._bottle_type)
        self._bottle_group.add(self._bottle_dropdown_row)

        self._bottle_name_row = Adw.EntryRow()
        self._bottle_name_row.set_title("Bottle Name")
        self._bottle_name_row.set_text("My First Bottle")
        self._bottle_group.add(self._bottle_name_row)

        self._create_bottle_btn = Gtk.Button(label="Create Bottle")
        self._create_bottle_btn.add_css_class("suggested-action")
        self._create_bottle_btn.set_halign(Gtk.Align.CENTER)
        self._create_bottle_btn.set_margin_top(8)
        self._create_bottle_btn.connect("clicked", self._on_create_bottle)
        self._outer_box.append(self._create_bottle_btn)

        # Progress label
        self._progress_label = Gtk.Label()
        self._progress_label.set_xalign(0)
        self._progress_label.set_wrap(True)
        self._progress_label.add_css_class("dim-label")
        self._progress_label.set_visible(False)
        self._outer_box.append(self._progress_label)

        self.add_navigation_buttons(back_tag="drivers", next_tag="timeshift")

    def _check_bottles_status(self) -> None:
        """Check if Bottles is already installed."""
        try:
            result = subprocess.run(
                ["flatpak", "info", "com.usebottles.bottles"],
                capture_output=True, text=True, timeout=10,
            )
            if result.returncode == 0:
                self._status_row.set_subtitle("Bottles is installed")
                self._status_row.add_prefix(
                    Gtk.Image.new_from_icon_name("emblem-ok-symbolic")
                )
                self._install_btn.set_label("Reinstall Bottles")
            else:
                self._status_row.set_subtitle("Bottles is not installed")
                self._status_row.add_prefix(
                    Gtk.Image.new_from_icon_name("dialog-information-symbolic")
                )
        except FileNotFoundError:
            self._status_row.set_subtitle("Flatpak is not installed")
            self._status_row.add_prefix(
                Gtk.Image.new_from_icon_name("dialog-warning-symbolic")
            )
        except Exception:
            self._status_row.set_subtitle("Could not check Bottles status")

    def _on_install(self, btn: Gtk.Button) -> None:
        btn.set_sensitive(False)
        self._spinner.set_visible(True)
        self._spinner.start()
        self._progress_label.set_text("Installing Bottles from Flathub...")
        self._progress_label.set_visible(True)

        # Install Bottles via Flatpak
        self.run_unprivileged(
            ["flatpak", "install", "--user", "-y", "flathub",
             "com.usebottles.bottles"],
            success_msg="Installed Bottles (Windows compatibility layer)",
            callback=self._on_bottles_installed,
        )

    def _on_bottles_installed(self, success: bool, output: str) -> None:
        if not success:
            self._progress_label.set_text(f"Installation failed.\n{output[:200]}")
            self._install_btn.set_sensitive(True)
            self._spinner.stop()
            self._spinner.set_visible(False)
            return

        self._progress_label.set_text("Bottles installed!")
        self._status_row.set_subtitle("Bottles is installed")

        # Now install optional deps sequentially (not in parallel)
        # to avoid multiple pkexec prompts
        want_wine = self._wine_check.get_active()
        want_gamemode = self._gamemode_check.get_active()

        if want_wine or want_gamemode:
            packages = []
            if want_wine:
                packages.extend(["wine64", "wine32", "libwine",
                                 "fonts-wine", "winetricks"])
            if want_gamemode:
                packages.append("gamemode")

            self._progress_label.set_text(
                f"Installing dependencies: {', '.join(packages)}..."
            )

            # Single privileged call for all deps
            # Use tempfile.mkstemp to avoid TOCTOU race conditions.
            script_lines = [
                "#!/bin/bash",
                "set -e",
                "export DEBIAN_FRONTEND=noninteractive",
                "dpkg --add-architecture i386 2>/dev/null || true",
                "apt-get update -qq",
                f"apt-get install -y {' '.join(packages)}",
            ]
            try:
                fd, script_path = tempfile.mkstemp(
                    prefix="first-steps-", suffix=".sh", dir="/tmp"
                )
                with os.fdopen(fd, "w") as f:
                    f.write("\n".join(script_lines) + "\n")
                os.chmod(script_path, 0o755)
            except Exception as e:
                self._progress_label.set_text(f"Error: {e}")
                self._finish_install()
                return

            desc_parts = []
            if want_wine:
                desc_parts.append("Wine system dependencies")
            if want_gamemode:
                desc_parts.append("GameMode")

            self.run_privileged(
                ["bash", script_path],
                success_msg=f"Installed {' and '.join(desc_parts)}",
                callback=lambda s, o: self._finish_install(),
            )
        else:
            self._finish_install()

    def _finish_install(self) -> None:
        self._spinner.stop()
        self._spinner.set_visible(False)
        self._install_btn.set_sensitive(True)
        self._progress_label.set_text(
            "Bottles is ready! You can create a bottle below or launch "
            "Bottles from your application menu."
        )
        self.show_toast("Bottles installed successfully!")

    def _on_create_bottle(self, btn: Gtk.Button) -> None:
        """Launch Bottles — bottle creation is handled by the Bottles GUI."""
        bottle_name = self._bottle_name_row.get_text().strip()
        if not bottle_name:
            self._progress_label.set_text("Please enter a name for your bottle.")
            self._progress_label.set_visible(True)
            return

        self._progress_label.set_text(
            f"Launching Bottles... Create your '{bottle_name}' bottle in the "
            f"Bottles interface that opens.\n\n"
            f"Tip: Bottles will download the necessary Wine runner on first launch. "
            f"This may take a few minutes."
        )
        self._progress_label.set_visible(True)

        self.window.log_action(f"Guided first-bottle setup: '{bottle_name}'")

        # Launch Bottles
        try:
            subprocess.Popen(
                ["flatpak", "run", "com.usebottles.bottles"],
                start_new_session=True,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
        except FileNotFoundError:
            self._progress_label.set_text(
                "Could not launch Bottles: flatpak not found.\n"
                "You can launch it from your application menu."
            )
        except Exception as e:
            self._progress_label.set_text(
                f"Could not launch Bottles: {e}\n"
                "You can launch it from your application menu."
            )

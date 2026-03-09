# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright 2026 First Steps Contributors
"""Auto-update module — checks GitHub Releases for new versions and offers in-app upgrade."""

import json
import os
import subprocess
import threading

import gi

gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")

from gi.repository import Adw, GLib, Gtk

from first_steps import __version__

GITHUB_REPO = "Naftaliro/first-steps"
RELEASES_API = f"https://api.github.com/repos/{GITHUB_REPO}/releases/latest"
DEB_FILENAME_PATTERN = "first-steps_{version}-1_all.deb"


def _parse_version(v: str) -> tuple[int, ...]:
    """Parse a version string like '1.1.0' into a comparable tuple."""
    v = v.lstrip("v").strip()
    parts = []
    for p in v.split("."):
        try:
            parts.append(int(p))
        except ValueError:
            parts.append(0)
    return tuple(parts)


class UpdateChecker:
    """Checks GitHub for a newer release and offers to install it."""

    def __init__(self, window: Adw.ApplicationWindow) -> None:
        self.window = window
        self._latest_version: str | None = None
        self._download_url: str | None = None

    def check_async(self) -> None:
        """Start a background check for updates. Shows a toast/dialog if an update is found."""
        thread = threading.Thread(target=self._check_worker, daemon=True)
        thread.start()

    def _check_worker(self) -> None:
        try:
            result = subprocess.run(
                ["curl", "-fsSL", "-H", "Accept: application/vnd.github+json",
                 "--connect-timeout", "10", "--max-time", "15",
                 RELEASES_API],
                capture_output=True, text=True, timeout=20,
            )
            if result.returncode != 0:
                return  # Silently fail — no network is fine

            data = json.loads(result.stdout)
            tag = data.get("tag_name", "")
            remote_version = tag.lstrip("v")

            if _parse_version(remote_version) <= _parse_version(__version__):
                return  # Already up to date

            # Find the .deb asset
            download_url = None
            for asset in data.get("assets", []):
                name = asset.get("name", "")
                if name.endswith(".deb"):
                    download_url = asset.get("browser_download_url")
                    break

            if not download_url:
                return  # No .deb in the release

            self._latest_version = remote_version
            self._download_url = download_url

            GLib.idle_add(self._show_update_dialog)

        except Exception:
            pass  # Silently fail — update check is best-effort

    def _show_update_dialog(self) -> None:
        """Show a dialog offering to update."""
        dialog = Adw.MessageDialog.new(
            self.window,
            "Update Available",
            f"First Steps v{self._latest_version} is available.\n"
            f"You are currently running v{__version__}.\n\n"
            f"Would you like to download and install the update?"
        )
        dialog.add_response("cancel", "Later")
        dialog.add_response("update", "Update Now")
        dialog.set_response_appearance("update", Adw.ResponseAppearance.SUGGESTED)
        dialog.set_default_response("update")
        dialog.connect("response", self._on_dialog_response)
        dialog.present()

    def _on_dialog_response(self, dialog, response: str) -> None:
        if response != "update":
            return
        self._do_update()

    def _do_update(self) -> None:
        """Download the new .deb and install it."""
        self.window.show_toast("Downloading update...")

        thread = threading.Thread(target=self._update_worker, daemon=True)
        thread.start()

    def _update_worker(self) -> None:
        tmp_deb = "/tmp/first-steps-update.deb"
        try:
            # Download
            result = subprocess.run(
                ["curl", "-fsSL", "-o", tmp_deb, self._download_url],
                capture_output=True, text=True, timeout=120,
            )
            if result.returncode != 0:
                GLib.idle_add(
                    self.window.show_toast,
                    "Download failed. Please update manually."
                )
                return

            # Install via pkexec
            result = subprocess.run(
                ["pkexec", "dpkg", "-i", tmp_deb],
                capture_output=True, text=True, timeout=120,
            )

            if result.returncode == 0:
                GLib.idle_add(self._show_restart_dialog)
            else:
                # Try apt fix
                subprocess.run(
                    ["pkexec", "apt-get", "install", "-f", "-y"],
                    capture_output=True, text=True, timeout=60,
                )
                GLib.idle_add(self._show_restart_dialog)

        except Exception as e:
            GLib.idle_add(
                self.window.show_toast,
                f"Update failed: {e}"
            )
        finally:
            try:
                os.unlink(tmp_deb)
            except OSError:
                pass

    def _show_restart_dialog(self) -> None:
        dialog = Adw.MessageDialog.new(
            self.window,
            "Update Installed",
            f"First Steps has been updated to v{self._latest_version}.\n"
            f"Please restart the application to use the new version."
        )
        dialog.add_response("ok", "OK")
        dialog.set_default_response("ok")
        dialog.present()

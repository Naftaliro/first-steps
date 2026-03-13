# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright 2026 Naftali Rosen
"""Welcome page — landing screen with system info and setup overview."""

import os
import platform
import subprocess

import gi

gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")

from gi.repository import Adw, GLib, Gtk

from first_steps.pages import BasePage


def _read_file(path: str) -> str:
    """Read a file and return its stripped content, or empty string."""
    try:
        with open(path) as f:
            return f.read().strip()
    except OSError:
        return ""


def _run_cmd(cmd: list[str]) -> str:
    """Run a command and return stdout, or empty string on failure."""
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=5)
        return r.stdout.strip() if r.returncode == 0 else ""
    except Exception:
        return ""


def _get_system_info() -> dict:
    """Gather system information in a background-safe way."""
    info = {}

    # OS
    os_release = _read_file("/etc/os-release")
    for line in os_release.splitlines():
        if line.startswith("PRETTY_NAME="):
            info["os"] = line.split("=", 1)[1].strip('"')
            break
    if "os" not in info:
        info["os"] = platform.platform()

    # Desktop environment
    info["desktop"] = os.environ.get("XDG_CURRENT_DESKTOP", "Unknown")

    # Kernel
    info["kernel"] = platform.release()

    # CPU
    cpu_info = _read_file("/proc/cpuinfo")
    for line in cpu_info.splitlines():
        if line.startswith("model name"):
            info["cpu"] = line.split(":", 1)[1].strip()
            break
    if "cpu" not in info:
        info["cpu"] = platform.processor() or "Unknown"

    # GPU — try lspci
    lspci = _run_cmd(["lspci"])
    gpus = []
    for line in lspci.splitlines():
        low = line.lower()
        if "vga" in low or "3d" in low or "display" in low:
            # Extract the device name after the colon
            parts = line.split(": ", 1)
            if len(parts) > 1:
                gpus.append(parts[1].strip())
    info["gpu"] = gpus[0] if gpus else "Unknown"
    if len(gpus) > 1:
        info["gpu"] += f" (+{len(gpus) - 1} more)"

    # RAM
    mem = _read_file("/proc/meminfo")
    for line in mem.splitlines():
        if line.startswith("MemTotal:"):
            kb = int(line.split()[1])
            info["ram"] = f"{round(kb / 1048576, 1)} GB"
            break
    if "ram" not in info:
        info["ram"] = "Unknown"

    # Disk — root partition
    try:
        st = os.statvfs("/")
        total = st.f_frsize * st.f_blocks
        avail = st.f_frsize * st.f_bavail
        info["disk"] = f"{round(avail / 1073741824, 1)} GB free of {round(total / 1073741824, 1)} GB"
    except OSError:
        info["disk"] = "Unknown"

    return info


class WelcomePage(BasePage):
    PAGE_TAG = "welcome"
    PAGE_TITLE = "Welcome"
    PAGE_ICON = "go-home-symbolic"

    def build_ui(self) -> None:
        # ── Hero icon ────────────────────────────────────────────────
        icon = Gtk.Image.new_from_icon_name("preferences-system-symbolic")
        icon.set_pixel_size(96)
        icon.add_css_class("dim-label")
        icon.set_margin_top(16)
        icon.set_margin_bottom(8)
        icon.set_halign(Gtk.Align.CENTER)
        self._outer_box.append(icon)

        # ── Title ────────────────────────────────────────────────────
        title_label = Gtk.Label(label="Welcome to First Steps")
        title_label.add_css_class("title-1")
        title_label.set_halign(Gtk.Align.CENTER)
        title_label.set_margin_bottom(4)
        self._outer_box.append(title_label)

        # ── Description ─────────────────────────────────────────────
        desc_text = (
            "Your system is almost ready. This wizard will help you "
            "install media codecs, set up Flatpak, detect drivers, "
            "configure backups, and more \u2014 all without touching a "
            "terminal.\n\n"
            "Work through each section at your own pace using the "
            "sidebar, or skip anything you don't need. Everything "
            "here is completely optional."
        )
        desc_label = Gtk.Label(label=desc_text)
        desc_label.set_wrap(True)
        desc_label.set_wrap_mode(2)  # WORD_CHAR
        desc_label.set_xalign(0)
        desc_label.set_halign(Gtk.Align.FILL)
        desc_label.add_css_class("body")
        desc_label.set_margin_start(4)
        desc_label.set_margin_end(4)
        desc_label.set_margin_bottom(8)
        self._outer_box.append(desc_label)

        # ── System info card ─────────────────────────────────────────
        self._sysinfo_group = self.add_preferences_group(
            "Your System",
            "Detected hardware and software:"
        )

        # Placeholder rows — will be populated async
        self._sysinfo_rows = {}
        fields = [
            ("computer-symbolic", "os", "Operating System", "Detecting..."),
            ("desktop-symbolic", "desktop", "Desktop Environment", "Detecting..."),
            ("processor-symbolic", "cpu", "Processor", "Detecting..."),
            ("video-display-symbolic", "gpu", "Graphics", "Detecting..."),
            ("memory-symbolic", "ram", "Memory", "Detecting..."),
            ("drive-harddisk-symbolic", "disk", "Disk Space", "Detecting..."),
            ("system-run-symbolic", "kernel", "Kernel", "Detecting..."),
        ]
        for icon_name, key, title, subtitle in fields:
            row = Adw.ActionRow()
            row.set_title(title)
            row.set_subtitle(subtitle)
            row.add_prefix(Gtk.Image.new_from_icon_name(icon_name))
            self._sysinfo_group.add(row)
            self._sysinfo_rows[key] = row

        # Fetch system info in background
        import threading
        threading.Thread(target=self._load_sysinfo, daemon=True).start()

        # ── Separator ────────────────────────────────────────────────
        sep = Gtk.Separator(orientation=Gtk.Orientation.HORIZONTAL)
        sep.set_margin_top(4)
        sep.set_margin_bottom(4)
        self._outer_box.append(sep)

        # ── Quick overview ───────────────────────────────────────────
        overview_title = Gtk.Label(label="What We Can Help You Set Up")
        overview_title.add_css_class("title-3")
        overview_title.set_halign(Gtk.Align.START)
        overview_title.set_margin_start(4)
        overview_title.set_margin_top(4)
        self._outer_box.append(overview_title)

        overview_desc = Gtk.Label(
            label="Each section handles a different part of your system setup:"
        )
        overview_desc.set_wrap(True)
        overview_desc.set_xalign(0)
        overview_desc.add_css_class("dim-label")
        overview_desc.set_margin_start(4)
        overview_desc.set_margin_bottom(8)
        self._outer_box.append(overview_desc)

        group = Adw.PreferencesGroup()
        self._outer_box.append(group)

        items = [
            ("media-playback-start-symbolic", "Codecs & Media",
             "Play any video or audio format out of the box"),
            ("system-software-install-symbolic", "Flatpak & Apps",
             "Enable Flathub and install popular applications"),
            ("preferences-system-symbolic", "Drivers",
             "Detect and install recommended hardware drivers"),
            ("preferences-desktop-apps-symbolic", "Windows Apps",
             "Run Windows software via Bottles"),
            ("drive-harddisk-symbolic", "Backup",
             "Set up automatic system snapshots with Timeshift"),
            ("battery-symbolic", "Power",
             "Configure power profiles and lid behavior"),
            ("security-high-symbolic", "Firewall",
             "Enable and configure UFW firewall"),
            ("network-wired-symbolic", "Network",
             "DNS, connectivity checks, and speed testing"),
            ("security-medium-symbolic", "Privacy",
             "Disable telemetry and harden privacy settings"),
            ("utilities-terminal-symbolic", "Development",
             "Set up Git, editors, Docker, and dev tools"),
            ("preferences-desktop-locale-symbolic", "Language",
             "Install language packs and input methods"),
            ("applications-utilities-symbolic", "Extras",
             "Theme switcher, system updates, and more"),
        ]

        for icon_name, row_title, subtitle in items:
            row = Adw.ActionRow()
            row.set_title(row_title)
            row.set_subtitle(subtitle)
            row.add_prefix(Gtk.Image.new_from_icon_name(icon_name))
            arrow = Gtk.Image.new_from_icon_name("go-next-symbolic")
            arrow.add_css_class("dim-label")
            row.add_suffix(arrow)
            group.add(row)

        # ── Get started button ───────────────────────────────────────
        get_started_btn = Gtk.Button(label="Get Started  \u2192")
        get_started_btn.add_css_class("suggested-action")
        get_started_btn.add_css_class("pill")
        get_started_btn.set_halign(Gtk.Align.CENTER)
        get_started_btn.set_margin_top(16)
        get_started_btn.set_margin_bottom(8)
        get_started_btn.connect(
            "clicked", lambda _: self.window.navigate_to("codecs")
        )
        self._outer_box.append(get_started_btn)

        # ── Version label ────────────────────────────────────────────
        from first_steps import __version__
        ver_label = Gtk.Label(label=f"First Steps v{__version__}")
        ver_label.add_css_class("dim-label")
        ver_label.add_css_class("caption")
        ver_label.set_margin_top(4)
        ver_label.set_margin_bottom(8)
        self._outer_box.append(ver_label)

    def _load_sysinfo(self) -> None:
        """Load system info in a background thread, then update UI."""
        info = _get_system_info()

        def _update():
            for key, row in self._sysinfo_rows.items():
                value = info.get(key, "Unknown")
                row.set_subtitle(value)

        GLib.idle_add(_update)

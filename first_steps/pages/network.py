# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright 2026 Naftali Rosen
"""Network & Connectivity page — DNS, connectivity checks, and speed testing."""

import subprocess
import threading
import time

import gi

gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")

from gi.repository import Adw, GLib, Gtk

from first_steps.pages import BasePage


class NetworkPage(BasePage):
    PAGE_TAG = "network"
    PAGE_TITLE = "Network"
    PAGE_ICON = "network-wired-symbolic"

    def build_ui(self) -> None:
        self.add_status_page(
            "network-wired-symbolic",
            "Network & Connectivity",
            "Check your connection, configure DNS, and test network speed."
        )

        # ── Connectivity check ───────────────────────────────────────
        self._conn_group = self.add_preferences_group(
            "Connectivity Status",
            "Check if your system can reach the internet:"
        )

        self._conn_row = Adw.ActionRow()
        self._conn_row.set_title("Internet Connection")
        self._conn_row.set_subtitle("Not checked yet")
        self._conn_row.add_prefix(
            Gtk.Image.new_from_icon_name("network-offline-symbolic")
        )
        self._conn_spinner = Gtk.Spinner()
        self._conn_spinner.set_visible(False)
        self._conn_row.add_suffix(self._conn_spinner)
        self._conn_group.add(self._conn_row)

        self._dns_row = Adw.ActionRow()
        self._dns_row.set_title("DNS Resolution")
        self._dns_row.set_subtitle("Not checked yet")
        self._dns_row.add_prefix(
            Gtk.Image.new_from_icon_name("network-server-symbolic")
        )
        self._conn_group.add(self._dns_row)

        self._latency_row = Adw.ActionRow()
        self._latency_row.set_title("Latency")
        self._latency_row.set_subtitle("Not checked yet")
        self._latency_row.add_prefix(
            Gtk.Image.new_from_icon_name("network-transmit-receive-symbolic")
        )
        self._conn_group.add(self._latency_row)

        check_btn = Gtk.Button(label="Run Connectivity Check")
        check_btn.add_css_class("suggested-action")
        check_btn.set_halign(Gtk.Align.CENTER)
        check_btn.connect("clicked", self._on_check_connectivity)
        self._outer_box.append(check_btn)

        # ── DNS configuration ────────────────────────────────────────
        dns_group = self.add_preferences_group(
            "DNS Configuration",
            "Set a faster or more private DNS resolver:"
        )

        self._dns_options = {}
        dns_providers = [
            ("Cloudflare", "1.1.1.1, 1.0.0.1", "Fast and privacy-focused"),
            ("Google", "8.8.8.8, 8.8.4.4", "Reliable with global coverage"),
            ("Quad9", "9.9.9.9, 149.112.112.112", "Security-focused, blocks malware"),
            ("System Default", "", "Use your router/ISP DNS"),
        ]

        group_btn = None
        for name, servers, desc in dns_providers:
            row = Adw.ActionRow()
            row.set_title(name)
            subtitle = desc
            if servers:
                subtitle += f" ({servers})"
            row.set_subtitle(subtitle)

            radio = Gtk.CheckButton()
            radio.set_valign(Gtk.Align.CENTER)
            if group_btn is None:
                group_btn = radio
                radio.set_active(True)  # Default selected
            else:
                radio.set_group(group_btn)

            row.add_prefix(radio)
            row.set_activatable_widget(radio)
            dns_group.add(row)
            self._dns_options[name] = (radio, servers)

        apply_dns_btn = Gtk.Button(label="Apply DNS Settings")
        apply_dns_btn.add_css_class("suggested-action")
        apply_dns_btn.set_halign(Gtk.Align.CENTER)
        apply_dns_btn.connect("clicked", self._on_apply_dns)
        self._outer_box.append(apply_dns_btn)

        # ── Useful network tools ─────────────────────────────────────
        tools_group = self.add_preferences_group(
            "Network Tools",
            "Install useful networking utilities:"
        )

        self._net_tools = {}
        tools = [
            ("net-tools", "Classic networking tools (ifconfig, netstat, etc.)"),
            ("traceroute", "Trace the route packets take to a host"),
            ("nmap", "Network scanner and security auditing tool"),
            ("curl", "Command-line HTTP client"),
            ("whois", "Domain name lookup utility"),
        ]

        for pkg, desc in tools:
            row, check = self.add_action_row_with_check(
                tools_group, pkg, desc
            )
            self._net_tools[pkg] = check

        install_tools_btn = Gtk.Button(label="Install Selected Tools")
        install_tools_btn.add_css_class("suggested-action")
        install_tools_btn.set_halign(Gtk.Align.CENTER)
        install_tools_btn.connect("clicked", self._on_install_tools)
        self._outer_box.append(install_tools_btn)

        self.add_navigation_buttons(back_tag="firewall", next_tag="privacy")

    def _on_check_connectivity(self, btn) -> None:
        """Run connectivity checks in background."""
        self._conn_spinner.set_visible(True)
        self._conn_spinner.start()
        self._conn_row.set_subtitle("Checking...")
        self._dns_row.set_subtitle("Checking...")
        self._latency_row.set_subtitle("Checking...")

        def _worker():
            results = {}

            # DNS check
            try:
                r = subprocess.run(
                    ["getent", "hosts", "github.com"],
                    capture_output=True, text=True, timeout=10
                )
                results["dns"] = r.returncode == 0
                if results["dns"]:
                    results["dns_ip"] = r.stdout.split()[0]
            except Exception:
                results["dns"] = False

            # HTTP connectivity check
            try:
                r = subprocess.run(
                    ["curl", "-sS", "-o", "/dev/null", "-w", "%{http_code}",
                     "--connect-timeout", "5", "https://connectivity-check.ubuntu.com"],
                    capture_output=True, text=True, timeout=10
                )
                results["http"] = r.stdout.strip() in ("200", "204", "301", "302")
            except Exception:
                results["http"] = False

            # Latency check (ping)
            try:
                r = subprocess.run(
                    ["ping", "-c", "3", "-W", "3", "1.1.1.1"],
                    capture_output=True, text=True, timeout=15
                )
                if r.returncode == 0:
                    # Parse avg latency from "rtt min/avg/max/mdev = ..."
                    for line in r.stdout.splitlines():
                        if "avg" in line and "/" in line:
                            parts = line.split("=")[1].strip().split("/")
                            results["latency"] = f"{parts[1]} ms (avg)"
                            break
                else:
                    results["latency"] = None
            except Exception:
                results["latency"] = None

            def _update():
                self._conn_spinner.stop()
                self._conn_spinner.set_visible(False)

                if results.get("http"):
                    self._conn_row.set_subtitle("Connected \u2714")
                else:
                    self._conn_row.set_subtitle("No connection \u2718")

                if results.get("dns"):
                    ip = results.get("dns_ip", "")
                    self._dns_row.set_subtitle(f"Working \u2714 (resolved to {ip})")
                else:
                    self._dns_row.set_subtitle("DNS resolution failed \u2718")

                lat = results.get("latency")
                if lat:
                    self._latency_row.set_subtitle(lat)
                else:
                    self._latency_row.set_subtitle("Could not measure latency")

                if results.get("http") and results.get("dns"):
                    self.mark_completed()
                    self.show_toast("Connectivity check passed")

            GLib.idle_add(_update)

        threading.Thread(target=_worker, daemon=True).start()

    def _on_apply_dns(self, btn) -> None:
        """Apply the selected DNS configuration via resolvconf or systemd-resolved."""
        selected = None
        servers = ""
        for name, (radio, srv) in self._dns_options.items():
            if radio.get_active():
                selected = name
                servers = srv
                break

        if not selected or selected == "System Default":
            self.show_toast("Using system default DNS")
            self.mark_completed()
            return

        # Build the DNS server list
        dns_list = [s.strip() for s in servers.split(",")]

        # Write a temporary script to configure DNS via systemd-resolved
        import tempfile
        script = "#!/bin/bash\nset -e\n"
        for dns in dns_list:
            script += f'echo "DNS={dns}" >> /etc/systemd/resolved.conf.d/first-steps-dns.conf\n'
        script += "mkdir -p /etc/systemd/resolved.conf.d\n"
        script_content = (
            "#!/bin/bash\nset -e\n"
            "mkdir -p /etc/systemd/resolved.conf.d\n"
            "cat > /etc/systemd/resolved.conf.d/first-steps-dns.conf << 'DNSEOF'\n"
            "[Resolve]\n"
        )
        for dns in dns_list:
            script_content += f"DNS={dns}\n"
        script_content += (
            "DNSEOF\n"
            "systemctl restart systemd-resolved 2>/dev/null || true\n"
        )

        with tempfile.NamedTemporaryFile(mode="w", suffix=".sh", delete=False) as f:
            f.write(script_content)
            tmp_path = f.name

        import os
        os.chmod(tmp_path, 0o755)

        def _done(success, output):
            try:
                os.unlink(tmp_path)
            except OSError:
                pass
            if success:
                self.show_toast(f"DNS set to {selected}")
            else:
                self.show_error_dialog("DNS Configuration Failed", output[:500])

        self.run_privileged(
            [tmp_path],
            f"Configured DNS: {selected} ({servers})",
            _done
        )

    def _on_install_tools(self, btn) -> None:
        """Install selected network tools."""
        selected = [pkg for pkg, check in self._net_tools.items() if check.get_active()]
        if not selected:
            self.show_toast("No tools selected")
            return

        import tempfile
        import os

        script = (
            "#!/bin/bash\nset -e\n"
            "export DEBIAN_FRONTEND=noninteractive\n"
            f"apt-get install -y {' '.join(selected)}\n"
        )

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
                self.show_toast(f"Installed: {', '.join(selected)}")
            else:
                self.show_error_dialog("Installation Failed", output[:500])

        self.run_privileged(
            [tmp_path],
            f"Installed network tools: {', '.join(selected)}",
            _done
        )

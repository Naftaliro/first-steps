# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright 2026 Naftali Rosen
"""Development Environment page — Git config, editors, Docker, and dev tools."""

import os
import subprocess
import tempfile
import threading

import gi

gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")

from gi.repository import Adw, GLib, Gtk

from first_steps.pages import BasePage


class DevelopmentPage(BasePage):
    PAGE_TAG = "development"
    PAGE_TITLE = "Development"
    PAGE_ICON = "utilities-terminal-symbolic"

    def build_ui(self) -> None:
        self.add_status_page(
            "utilities-terminal-symbolic",
            "Development Environment",
            "Set up your development tools \u2014 Git identity, code editors, "
            "container runtimes, and programming languages."
        )

        # ── Git configuration ────────────────────────────────────────
        git_group = self.add_preferences_group(
            "Git Configuration",
            "Set your global Git identity (used for commits):"
        )

        # Git name
        self._git_name_row = Adw.EntryRow()
        self._git_name_row.set_title("Full Name")
        # Pre-fill from existing config
        existing_name = self._get_git_config("user.name")
        if existing_name:
            self._git_name_row.set_text(existing_name)
        git_group.add(self._git_name_row)

        # Git email
        self._git_email_row = Adw.EntryRow()
        self._git_email_row.set_title("Email Address")
        existing_email = self._get_git_config("user.email")
        if existing_email:
            self._git_email_row.set_text(existing_email)
        git_group.add(self._git_email_row)

        # Default branch
        self._git_branch_row = Adw.EntryRow()
        self._git_branch_row.set_title("Default Branch Name")
        self._git_branch_row.set_text(
            self._get_git_config("init.defaultBranch") or "main"
        )
        git_group.add(self._git_branch_row)

        apply_git_btn = Gtk.Button(label="Apply Git Configuration")
        apply_git_btn.add_css_class("suggested-action")
        apply_git_btn.set_halign(Gtk.Align.CENTER)
        apply_git_btn.connect("clicked", self._on_apply_git)
        self._outer_box.append(apply_git_btn)

        # ── Code editors (Flatpak) ───────────────────────────────────
        editors_group = self.add_preferences_group(
            "Code Editors",
            "Install popular editors via Flatpak:"
        )

        self._editors = {}
        editors = [
            ("com.visualstudio.code", "Visual Studio Code",
             "Microsoft's popular code editor"),
            ("com.vscodium.codium", "VSCodium",
             "VS Code without Microsoft telemetry"),
            ("io.neovim.nvim", "Neovim (Flatpak)",
             "Hyperextensible Vim-based text editor"),
            ("org.gnome.Builder", "GNOME Builder",
             "IDE for GNOME application development"),
            ("dev.zed.Zed", "Zed",
             "High-performance multiplayer code editor"),
        ]

        for app_id, name, desc in editors:
            row, check = self.add_action_row_with_check(
                editors_group, name, desc
            )
            self._editors[app_id] = check

        install_editors_btn = Gtk.Button(label="Install Selected Editors")
        install_editors_btn.add_css_class("suggested-action")
        install_editors_btn.set_halign(Gtk.Align.CENTER)
        install_editors_btn.connect("clicked", self._on_install_editors)
        self._outer_box.append(install_editors_btn)

        # ── Container & VM tools ─────────────────────────────────────
        container_group = self.add_preferences_group(
            "Containers & Virtualization",
            "Install container runtimes and VM tools:"
        )

        self._containers = {}
        container_tools = [
            ("docker.io", "Docker",
             "Industry-standard container runtime"),
            ("docker-compose", "Docker Compose",
             "Multi-container orchestration tool"),
            ("podman", "Podman",
             "Daemonless container engine (rootless)"),
            ("virt-manager", "Virtual Machine Manager",
             "GUI for managing KVM/QEMU virtual machines"),
        ]

        for pkg, name, desc in container_tools:
            row, check = self.add_action_row_with_check(
                container_group, name, desc
            )
            self._containers[pkg] = check

        install_containers_btn = Gtk.Button(label="Install Selected Tools")
        install_containers_btn.add_css_class("suggested-action")
        install_containers_btn.set_halign(Gtk.Align.CENTER)
        install_containers_btn.connect("clicked", self._on_install_containers)
        self._outer_box.append(install_containers_btn)

        # ── Programming languages ────────────────────────────────────
        lang_group = self.add_preferences_group(
            "Programming Languages & Runtimes",
            "Install language runtimes and package managers:"
        )

        self._languages = {}
        languages = [
            ("python3-pip python3-venv", "Python (pip + venv)",
             "Python package manager and virtual environments"),
            ("nodejs npm", "Node.js + npm",
             "JavaScript runtime and package manager"),
            ("rustc cargo", "Rust (rustc + cargo)",
             "Systems programming language"),
            ("golang-go", "Go",
             "Google's compiled programming language"),
            ("default-jdk", "Java (OpenJDK)",
             "Java Development Kit"),
        ]

        for pkgs, name, desc in languages:
            row, check = self.add_action_row_with_check(
                lang_group, name, desc
            )
            self._languages[pkgs] = check

        install_langs_btn = Gtk.Button(label="Install Selected Languages")
        install_langs_btn.add_css_class("suggested-action")
        install_langs_btn.set_halign(Gtk.Align.CENTER)
        install_langs_btn.connect("clicked", self._on_install_languages)
        self._outer_box.append(install_langs_btn)

        # ── Useful dev utilities ─────────────────────────────────────
        utils_group = self.add_preferences_group(
            "Developer Utilities",
            "Handy tools for development:"
        )

        self._dev_utils = {}
        utils = [
            ("build-essential", "Build Essential",
             "GCC, G++, make, and other compilation tools"),
            ("git-lfs", "Git LFS",
             "Git extension for large file storage"),
            ("jq", "jq",
             "Command-line JSON processor"),
            ("httpie", "HTTPie",
             "User-friendly HTTP client for the terminal"),
            ("shellcheck", "ShellCheck",
             "Static analysis tool for shell scripts"),
        ]

        for pkg, name, desc in utils:
            row, check = self.add_action_row_with_check(
                utils_group, name, desc
            )
            self._dev_utils[pkg] = check

        install_utils_btn = Gtk.Button(label="Install Selected Utilities")
        install_utils_btn.add_css_class("suggested-action")
        install_utils_btn.set_halign(Gtk.Align.CENTER)
        install_utils_btn.connect("clicked", self._on_install_dev_utils)
        self._outer_box.append(install_utils_btn)

        self.add_navigation_buttons(back_tag="privacy", next_tag="language")

    @staticmethod
    def _get_git_config(key: str) -> str:
        """Read a git config value, return empty string on failure."""
        try:
            r = subprocess.run(
                ["git", "config", "--global", key],
                capture_output=True, text=True, timeout=5
            )
            return r.stdout.strip() if r.returncode == 0 else ""
        except Exception:
            return ""

    def _on_apply_git(self, btn) -> None:
        """Apply Git global configuration."""
        name = self._git_name_row.get_text().strip()
        email = self._git_email_row.get_text().strip()
        branch = self._git_branch_row.get_text().strip() or "main"

        if not name or not email:
            self.show_toast("Please enter both name and email")
            return

        changes = []
        try:
            subprocess.run(
                ["git", "config", "--global", "user.name", name],
                capture_output=True, timeout=5
            )
            changes.append(f"name={name}")

            subprocess.run(
                ["git", "config", "--global", "user.email", email],
                capture_output=True, timeout=5
            )
            changes.append(f"email={email}")

            subprocess.run(
                ["git", "config", "--global", "init.defaultBranch", branch],
                capture_output=True, timeout=5
            )
            changes.append(f"branch={branch}")

            self.window.log_action(
                f"Configured Git: {name} <{email}>, default branch: {branch}"
            )
            self.mark_completed()
            self.show_toast("Git configuration applied")
        except Exception as e:
            self.show_error_dialog("Git Configuration Failed", str(e))

    def _on_install_editors(self, btn) -> None:
        """Install selected code editors via Flatpak."""
        selected = [
            app_id for app_id, check in self._editors.items()
            if check.get_active()
        ]
        if not selected:
            self.show_toast("No editors selected")
            return

        # Install sequentially via flatpak
        cmd = ["flatpak", "install", "--user", "-y", "flathub"] + selected

        def _done(success, output):
            if success:
                names = [a.split(".")[-1] for a in selected]
                self.show_toast(f"Installed: {', '.join(names)}")
            else:
                self.show_error_dialog("Installation Failed", output[:500])

        self.run_unprivileged(
            cmd,
            f"Installed editors: {', '.join(selected)}",
            _done
        )

    def _on_install_containers(self, btn) -> None:
        """Install selected container/VM tools."""
        selected = [
            pkg for pkg, check in self._containers.items()
            if check.get_active()
        ]
        if not selected:
            self.show_toast("No tools selected")
            return

        script = (
            "#!/bin/bash\nset -e\n"
            "export DEBIAN_FRONTEND=noninteractive\n"
            f"apt-get install -y {' '.join(selected)}\n"
        )

        # Add user to docker group if docker is being installed
        if "docker.io" in selected:
            user = os.environ.get("USER", "")
            if user:
                script += f"usermod -aG docker {user} 2>/dev/null || true\n"

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
                msg = f"Installed: {', '.join(selected)}"
                if "docker.io" in selected:
                    msg += " (log out and back in for Docker group)"
                self.show_toast(msg)
            else:
                self.show_error_dialog("Installation Failed", output[:500])

        self.run_privileged(
            [tmp_path],
            f"Installed container tools: {', '.join(selected)}",
            _done
        )

    def _on_install_languages(self, btn) -> None:
        """Install selected programming language runtimes."""
        selected_pkgs = []
        selected_names = []
        for pkgs, check in self._languages.items():
            if check.get_active():
                selected_pkgs.extend(pkgs.split())
                selected_names.append(pkgs.split()[0])

        if not selected_pkgs:
            self.show_toast("No languages selected")
            return

        script = (
            "#!/bin/bash\nset -e\n"
            "export DEBIAN_FRONTEND=noninteractive\n"
            f"apt-get install -y {' '.join(selected_pkgs)}\n"
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
                self.show_toast(f"Installed: {', '.join(selected_names)}")
            else:
                self.show_error_dialog("Installation Failed", output[:500])

        self.run_privileged(
            [tmp_path],
            f"Installed languages: {', '.join(selected_names)}",
            _done
        )

    def _on_install_dev_utils(self, btn) -> None:
        """Install selected developer utilities."""
        selected = [
            pkg for pkg, check in self._dev_utils.items()
            if check.get_active()
        ]
        if not selected:
            self.show_toast("No utilities selected")
            return

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
            f"Installed dev utilities: {', '.join(selected)}",
            _done
        )

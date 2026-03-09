# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright 2026 Naftali Rosen
"""Tests for file integrity, license headers, and project structure.

These tests verify that all source files have proper license headers,
the project structure is complete, and packaging files are valid.
"""

import os
import glob

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def get_project_files(pattern: str) -> list[str]:
    """Get project files matching a glob pattern, excluding .git and packaging/deb."""
    files = glob.glob(os.path.join(PROJECT_ROOT, pattern), recursive=True)
    return [
        f for f in files
        if "/.git/" not in f and "/packaging/deb/first-steps_" not in f
        and "/__pycache__/" not in f
    ]


class TestLicenseHeaders:
    """Every source file must have an SPDX license header."""

    def test_python_files_have_spdx(self):
        """All Python files must have SPDX-License-Identifier."""
        py_files = get_project_files("**/*.py")
        assert len(py_files) > 0, "No Python files found"
        for filepath in py_files:
            with open(filepath) as f:
                content = f.read(200)
            assert "SPDX-License-Identifier" in content, (
                f"Missing SPDX header in {os.path.relpath(filepath, PROJECT_ROOT)}"
            )

    def test_shell_files_have_spdx(self):
        """All shell scripts must have SPDX-License-Identifier."""
        sh_files = get_project_files("**/*.sh")
        sh_files.extend(get_project_files("**/first-steps-helper"))
        assert len(sh_files) > 0, "No shell files found"
        for filepath in sh_files:
            with open(filepath) as f:
                content = f.read(500)
            assert "SPDX-License-Identifier" in content, (
                f"Missing SPDX header in {os.path.relpath(filepath, PROJECT_ROOT)}"
            )

    def test_desktop_file_has_spdx(self):
        """Desktop entry must have SPDX-License-Identifier."""
        desktop = os.path.join(PROJECT_ROOT, "data", "io.github.firststeps.desktop")
        with open(desktop) as f:
            content = f.read(200)
        assert "SPDX-License-Identifier" in content


class TestProjectStructure:
    """The project must have all required files and directories."""

    REQUIRED_FILES = [
        "LICENSE",
        "README.md",
        "NOTICE",
        "CONTRIBUTING.md",
        "CODE_OF_CONDUCT.md",
        "LICENSING-AUDIT.md",
        ".gitignore",
        "install.sh",
        "first_steps/__init__.py",
        "first_steps/app.py",
        "first_steps/updater.py",
        "first_steps/pages/__init__.py",
        "first_steps/pages/welcome.py",
        "first_steps/pages/codecs.py",
        "first_steps/pages/flatpak.py",
        "first_steps/pages/drivers.py",
        "first_steps/pages/bottles.py",
        "first_steps/pages/timeshift.py",
        "first_steps/pages/power.py",
        "first_steps/pages/firewall.py",
        "first_steps/pages/extras.py",
        "first_steps/pages/summary.py",
        "scripts/first-steps-helper",
        "scripts/install-online.sh",
        "data/io.github.firststeps.desktop",
        "data/io.github.firststeps.policy",
        "data/io.github.firststeps.metainfo.xml",
        "data/icons/hicolor/scalable/apps/io.github.firststeps.svg",
        "packaging/build-deb.sh",
        ".github/workflows/ci.yml",
        ".github/workflows/release.yml",
    ]

    def test_all_required_files_exist(self):
        """Every required file must exist in the project."""
        missing = []
        for rel_path in self.REQUIRED_FILES:
            full_path = os.path.join(PROJECT_ROOT, rel_path)
            if not os.path.isfile(full_path):
                missing.append(rel_path)
        assert len(missing) == 0, f"Missing files: {', '.join(missing)}"

    def test_license_file_is_gpl3(self):
        """LICENSE file must contain GPL-3.0 text."""
        license_path = os.path.join(PROJECT_ROOT, "LICENSE")
        with open(license_path) as f:
            content = f.read(500)
        assert "GNU GENERAL PUBLIC LICENSE" in content
        assert "Version 3" in content

    def test_install_script_is_executable(self):
        """install.sh must be executable."""
        install_path = os.path.join(PROJECT_ROOT, "install.sh")
        assert os.access(install_path, os.X_OK)

    def test_build_deb_script_is_executable(self):
        """build-deb.sh must be executable."""
        build_path = os.path.join(PROJECT_ROOT, "packaging", "build-deb.sh")
        assert os.access(build_path, os.X_OK)


class TestDesktopEntry:
    """The desktop entry file must be valid."""

    def test_desktop_entry_has_required_keys(self):
        """Desktop entry must have Name, Exec, Icon, Type."""
        desktop_path = os.path.join(
            PROJECT_ROOT, "data", "io.github.firststeps.desktop"
        )
        with open(desktop_path) as f:
            content = f.read()

        required_keys = ["Name=", "Exec=", "Icon=", "Type="]
        for key in required_keys:
            assert key in content, f"Missing key '{key}' in desktop entry"

    def test_desktop_entry_exec_is_correct(self):
        """Desktop entry Exec must point to first-steps."""
        desktop_path = os.path.join(
            PROJECT_ROOT, "data", "io.github.firststeps.desktop"
        )
        with open(desktop_path) as f:
            for line in f:
                if line.startswith("Exec="):
                    assert "first-steps" in line
                    return
        assert False, "No Exec= line found"


class TestPolkitPolicy:
    """The polkit policy file must be valid XML with correct action ID."""

    def test_policy_has_correct_action_id(self):
        """Policy must define the io.github.firststeps.pkexec.run-helper action."""
        policy_path = os.path.join(
            PROJECT_ROOT, "data", "io.github.firststeps.policy"
        )
        with open(policy_path) as f:
            content = f.read()
        assert "io.github.firststeps.pkexec.run-helper" in content

    def test_policy_references_helper_path(self):
        """Policy must reference the correct helper script path."""
        policy_path = os.path.join(
            PROJECT_ROOT, "data", "io.github.firststeps.policy"
        )
        with open(policy_path) as f:
            content = f.read()
        assert "/usr/lib/first-steps/first-steps-helper" in content

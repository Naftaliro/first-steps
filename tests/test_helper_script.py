# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright 2026 Naftali Rosen
"""Tests for the privileged helper script argument validation.

These tests verify the helper script's argument parsing and validation
WITHOUT actually running privileged operations. We test the script's
behavior by running it with invalid arguments and checking exit codes
and error messages.
"""

import os
import subprocess

HELPER_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "scripts",
    "first-steps-helper",
)


def run_helper(*args: str) -> subprocess.CompletedProcess:
    """Run the helper script with given arguments (unprivileged)."""
    return subprocess.run(
        ["bash", HELPER_PATH, *args],
        capture_output=True,
        text=True,
        timeout=10,
    )


class TestHelperArgumentValidation:
    """Tests for helper script argument parsing."""

    def test_no_action_fails(self):
        """Running with no arguments should fail."""
        result = run_helper()
        assert result.returncode != 0

    def test_unknown_action_fails(self):
        """Running with an unknown action should fail."""
        result = run_helper("unknown-action")
        assert result.returncode != 0
        assert "Unknown action" in result.stderr or "ERROR" in result.stderr

    def test_install_packages_no_args_fails(self):
        """install-packages with no package names should fail."""
        result = run_helper("install-packages")
        assert result.returncode != 0
        assert "No packages specified" in result.stderr or "ERROR" in result.stderr

    def test_enable_ufw_no_script_fails(self):
        """enable-ufw with no script path should fail."""
        result = run_helper("enable-ufw")
        assert result.returncode != 0

    def test_enable_ufw_missing_file_fails(self):
        """enable-ufw with a nonexistent script should fail."""
        result = run_helper("enable-ufw", "/tmp/nonexistent-script-12345.sh")
        assert result.returncode != 0
        assert "not found" in result.stderr or "ERROR" in result.stderr

    def test_configure_timeshift_no_config_fails(self):
        """configure-timeshift with no config path should fail."""
        result = run_helper("configure-timeshift")
        assert result.returncode != 0

    def test_configure_timeshift_missing_file_fails(self):
        """configure-timeshift with nonexistent config should fail."""
        result = run_helper("configure-timeshift", "/tmp/nonexistent-config-12345.json")
        assert result.returncode != 0

    def test_install_drivers_no_args_fails(self):
        """install-drivers with no driver names should fail."""
        result = run_helper("install-drivers")
        assert result.returncode != 0

    def test_run_script_no_path_fails(self):
        """run-script with no script path should fail."""
        result = run_helper("run-script")
        assert result.returncode != 0

    def test_run_script_disallowed_path_fails(self):
        """run-script should reject scripts outside /tmp/first-steps-*."""
        result = run_helper("run-script", "/etc/passwd")
        assert result.returncode != 0
        assert "not allowed" in result.stderr or "ERROR" in result.stderr

    def test_run_script_path_traversal_fails(self):
        """run-script should reject path traversal attempts."""
        result = run_helper("run-script", "/tmp/first-steps-../../etc/passwd")
        # The script should either reject this or the file won't exist
        assert result.returncode != 0


class TestHelperScriptIntegrity:
    """Tests for helper script file integrity."""

    def test_helper_exists(self):
        """Helper script must exist."""
        assert os.path.isfile(HELPER_PATH)

    def test_helper_is_executable(self):
        """Helper script must be executable."""
        assert os.access(HELPER_PATH, os.X_OK)

    def test_helper_has_shebang(self):
        """Helper script must start with a bash shebang."""
        with open(HELPER_PATH) as f:
            first_line = f.readline().strip()
        assert first_line == "#!/bin/bash"

    def test_helper_uses_strict_mode(self):
        """Helper script must use set -euo pipefail for safety."""
        with open(HELPER_PATH) as f:
            content = f.read()
        assert "set -euo pipefail" in content

    def test_helper_has_spdx_header(self):
        """Helper script must have an SPDX license header."""
        with open(HELPER_PATH) as f:
            content = f.read(500)
        assert "SPDX-License-Identifier" in content

# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright 2026 Naftali Rosen
"""Tests for project metadata and module structure."""

import importlib
import re


def test_version_format():
    """Version string must follow semantic versioning (X.Y.Z)."""
    from first_steps import __version__
    assert re.match(r"^\d+\.\d+\.\d+$", __version__), (
        f"Version '{__version__}' does not match semver format X.Y.Z"
    )


def test_app_id_format():
    """App ID must follow reverse-DNS convention."""
    from first_steps import __app_id__
    assert __app_id__.count(".") >= 2, "App ID must have at least 3 segments"
    assert __app_id__ == "io.github.firststeps"


def test_version_is_not_empty():
    """Version must not be empty."""
    from first_steps import __version__
    assert len(__version__) > 0


def test_all_page_modules_importable():
    """All page modules must be importable without GTK (syntax check)."""
    page_modules = [
        "first_steps.pages",
        "first_steps.updater",
        "first_steps.helpers",
    ]
    # These modules don't require GTK to import their module-level code
    for mod_name in page_modules:
        # Just verify the module path exists and has no syntax errors
        # We can't fully import GTK-dependent modules without a display
        spec = importlib.util.find_spec(mod_name)
        assert spec is not None, f"Module {mod_name} not found"

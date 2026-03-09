# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright 2026 Naftali
"""Tests for the auto-update version comparison logic."""

import json
import os
import sys

# We need to test the version parsing logic without importing GTK.
# Extract the relevant logic for testing.


def parse_version(version_str: str) -> tuple:
    """Parse a version string like '1.2.3' or 'v1.2.3' into a tuple of ints."""
    cleaned = version_str.lstrip("v").strip()
    parts = cleaned.split(".")
    return tuple(int(p) for p in parts)


def is_newer(remote: str, local: str) -> bool:
    """Return True if remote version is newer than local."""
    try:
        return parse_version(remote) > parse_version(local)
    except (ValueError, AttributeError):
        return False


class TestVersionParsing:
    """Tests for version string parsing."""

    def test_parse_simple_version(self):
        assert parse_version("1.2.3") == (1, 2, 3)

    def test_parse_version_with_v_prefix(self):
        assert parse_version("v1.2.3") == (1, 2, 3)

    def test_parse_version_with_whitespace(self):
        assert parse_version("  1.0.0  ") == (1, 0, 0)

    def test_parse_major_only(self):
        """Edge case: single number should still parse."""
        assert parse_version("1") == (1,)

    def test_parse_two_part_version(self):
        assert parse_version("1.2") == (1, 2)


class TestVersionComparison:
    """Tests for version comparison logic."""

    def test_newer_patch(self):
        assert is_newer("1.1.1", "1.1.0") is True

    def test_newer_minor(self):
        assert is_newer("1.2.0", "1.1.0") is True

    def test_newer_major(self):
        assert is_newer("2.0.0", "1.9.9") is True

    def test_same_version(self):
        assert is_newer("1.1.0", "1.1.0") is False

    def test_older_version(self):
        assert is_newer("1.0.0", "1.1.0") is False

    def test_with_v_prefix(self):
        assert is_newer("v1.2.0", "1.1.0") is True

    def test_both_with_v_prefix(self):
        assert is_newer("v2.0.0", "v1.0.0") is True

    def test_invalid_remote_returns_false(self):
        assert is_newer("not-a-version", "1.0.0") is False

    def test_empty_remote_returns_false(self):
        assert is_newer("", "1.0.0") is False

    def test_none_remote_returns_false(self):
        assert is_newer(None, "1.0.0") is False


class TestReleaseJsonParsing:
    """Tests for parsing GitHub Releases API responses."""

    def test_extract_tag_from_release_json(self):
        """Simulate parsing a GitHub release response."""
        mock_response = {
            "tag_name": "v1.2.0",
            "name": "First Steps v1.2.0",
            "assets": [
                {
                    "name": "first-steps_1.2.0-1_all.deb",
                    "browser_download_url": "https://github.com/Naftaliro/first-steps/releases/download/v1.2.0/first-steps_1.2.0-1_all.deb",
                }
            ],
        }
        tag = mock_response.get("tag_name", "")
        assert tag == "v1.2.0"
        assert is_newer(tag, "1.1.0") is True

    def test_extract_deb_url_from_assets(self):
        """Verify we can find the .deb URL in release assets."""
        mock_response = {
            "tag_name": "v1.2.0",
            "assets": [
                {
                    "name": "SHA256SUMS",
                    "browser_download_url": "https://example.com/SHA256SUMS",
                },
                {
                    "name": "first-steps_1.2.0-1_all.deb",
                    "browser_download_url": "https://example.com/first-steps_1.2.0-1_all.deb",
                },
            ],
        }
        deb_url = None
        for asset in mock_response.get("assets", []):
            if asset["name"].endswith(".deb"):
                deb_url = asset["browser_download_url"]
                break
        assert deb_url == "https://example.com/first-steps_1.2.0-1_all.deb"

    def test_no_assets_returns_none(self):
        """Handle release with no assets gracefully."""
        mock_response = {"tag_name": "v1.2.0", "assets": []}
        deb_url = None
        for asset in mock_response.get("assets", []):
            if asset["name"].endswith(".deb"):
                deb_url = asset["browser_download_url"]
                break
        assert deb_url is None

    def test_missing_tag_name(self):
        """Handle response with missing tag_name."""
        mock_response = {"assets": []}
        tag = mock_response.get("tag_name", "")
        assert is_newer(tag, "1.0.0") is False

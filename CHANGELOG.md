# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.1.0] - 2026

### Added
- Auto-update feature: checks GitHub Releases for new versions and offers in-app upgrade.
- Update checker module (`first_steps/updater.py`).
- `.deb` packaging with `build-deb.sh` script.
- Online installer script (`scripts/install-online.sh`).
- Comprehensive test suite (`tests/`).
- LICENSING-AUDIT.md with full dependency and trademark analysis.
- NOTICE file for third-party attribution.

### Changed
- Improved error handling across all wizard pages.

## [1.0.0] - 2026

### Added
- Initial release of First Steps onboarding wizard.
- GTK4 + LibAdwaita UI with wizard-style navigation.
- Wizard pages: Welcome, Codecs, Flatpak, Drivers, Bottles, Timeshift, Power, Firewall, Extras, Summary.
- Privileged helper script with polkit integration.
- AppStream metainfo and desktop entry.
- Source install script (`install.sh`).
- GPL-3.0-or-later licensing with SPDX headers on all source files.

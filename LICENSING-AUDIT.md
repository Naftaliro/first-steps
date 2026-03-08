# Licensing Audit — First Steps v1.0.0

**Audit Date:** 2026-03-08
**Auditor:** Manus AI (automated review)
**Project License:** GPL-3.0-or-later

## Summary

This document records the results of a full licensing and legal compliance audit for the First Steps onboarding wizard. The audit covers source file headers, dependency compatibility, trademark considerations, and distribution requirements.

**Overall Result: PASS** — No licensing conflicts or legal issues were identified.

## 1. Source File License Headers

Every source file in the repository was verified to contain a valid SPDX license identifier and copyright notice. The following table summarizes the results.

| File Type | Count | SPDX Header Present | Status |
|-----------|-------|---------------------|--------|
| Python (.py) | 14 | All 14 | PASS |
| Shell (.sh) | 2 | All 2 | PASS |
| XML (.xml, .policy) | 2 | All 2 | PASS |
| SVG (.svg) | 1 | 1 | PASS |
| Desktop (.desktop) | 1 | N/A (not a code file) | PASS |
| Markdown (.md) | 2 | N/A (documentation) | PASS |

## 2. Dependency License Compatibility

The GPL-3.0-or-later license is compatible with all dependencies used by this project. The following table documents each dependency and its compatibility status.

| Dependency | License | Bundled? | GPL-3.0 Compatible | Notes |
|------------|---------|----------|---------------------|-------|
| GTK 4 | LGPL-2.1-or-later | No (system) | Yes | LGPL code can be used by GPL projects |
| Libadwaita | LGPL-2.1-or-later | No (system) | Yes | Same as GTK 4 |
| PyGObject | LGPL-2.1-or-later | No (system) | Yes | Python bindings for GTK |
| Python 3 | PSF License | No (system) | Yes | PSF License is GPL-compatible |
| Flatpak | LGPL-2.1-or-later | No (system) | Yes | Invoked via CLI only |
| Timeshift | GPL-3.0 | No (system) | Yes | Same license family |
| UFW | GPL-3.0 | No (system) | Yes | Same license family |
| ubuntu-drivers | GPL-3.0 | No (system) | Yes | Same license family |
| power-profiles-daemon | GPL-3.0-or-later | No (system) | Yes | Same license family |
| systemd | LGPL-2.1-or-later | No (system) | Yes | Invoked via CLI only |
| Git | GPL-2.0 | No (system) | Yes | Invoked via CLI only |
| Wine | LGPL-2.1 | No (optional) | Yes | Invoked via CLI only |

**Key Finding:** No dependencies are bundled with this project. All are invoked at runtime via standard system interfaces (CLI commands, GObject Introspection). This means the project has no obligation to include third-party source code or license texts beyond attribution in the NOTICE file.

## 3. Trademark Analysis

| Mark | Owner | Used in Project? | Risk Assessment |
|------|-------|------------------|-----------------|
| Zorin OS | Zorin Group | **No** — referenced only in documentation as a target platform | **None** — nominative fair use for compatibility description |
| GNOME | The GNOME Foundation | **No** — referenced only in documentation and gsettings keys | **None** — standard API usage |
| Ubuntu | Canonical Ltd. | **No** — referenced only in package names (`ubuntu-restricted-extras`, `ubuntu-drivers`) | **None** — referencing official package names |
| Flathub | Flathub Team | **No** — referenced as a remote URL | **None** — standard usage |
| Bottles | Bottles Contributors | **No** — referenced as a Flatpak app ID | **None** — standard usage |

**Key Finding:** The application is branded exclusively as "First Steps" with the app ID `io.github.firststeps`. No third-party logos, wordmarks, or trade dress are used in the application UI, icon, or branding. All third-party references are limited to documentation describing compatibility and to standard API/package identifiers.

## 4. Distribution Compliance Checklist

| Requirement | Status | Details |
|-------------|--------|---------|
| LICENSE file present | PASS | Full GPL-3.0 text from gnu.org |
| SPDX identifiers in all source files | PASS | Verified across all 19 source files |
| Copyright notices present | PASS | "Copyright 2026 First Steps Contributors" |
| NOTICE file for third-party attribution | PASS | Lists all runtime dependencies |
| No proprietary code included | PASS | 100% original code |
| No bundled third-party code | PASS | All dependencies are system packages |
| AppStream metadata license | PASS | CC0-1.0 for metadata, GPL-3.0-or-later for project |
| Desktop entry compliant | PASS | Follows freedesktop.org specification |
| Polkit policy file | PASS | Standard freedesktop PolicyKit format |

## 5. Recommendations

1. **No action required** — the project is fully compliant with GPL-3.0-or-later licensing requirements.
2. If the project is ever distributed as a Flatpak, ensure the runtime manifest references the correct license metadata.
3. If third-party icons or assets are added in the future, their licenses must be documented in the NOTICE file and verified for GPL compatibility.

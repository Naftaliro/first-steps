# Licensing Audit — First Steps v1.1.0

**Audit Date:** 2026-03-08
**Auditor:** Automated + Manual Review
**Project License:** GPL-3.0-or-later
**SPDX Identifier:** `GPL-3.0-or-later`

## Summary

This document records the results of a full licensing and legal compliance audit for the First Steps onboarding wizard v1.1.0. The audit covers source file headers, dependency compatibility, trademark considerations, auto-update compliance, and distribution requirements.

**Overall Result: PASS** — No licensing conflicts or legal issues were identified.

## 1. Source File License Headers

Every source file in the repository was verified to contain a valid SPDX license identifier and copyright notice. The following table summarizes the results.

| File Type | Count | SPDX Header Present | Status |
|-----------|-------|---------------------|--------|
| Python (.py) | 15 | All 15 | PASS |
| Shell scripts (.sh, helper) | 4 | All 4 | PASS |
| XML (.policy, .metainfo.xml) | 2 | All 2 | PASS |
| SVG (.svg) | 1 | 1 | PASS |
| Desktop entry (.desktop) | 1 | 1 | PASS |

**Total files with license headers: 23/23 — 100% coverage**

## 2. Dependency License Compatibility

The GPL-3.0-or-later license is compatible with all dependencies used by this project. The following table documents each dependency and its compatibility status.

| Dependency | License | Bundled? | GPL-3.0 Compatible | Notes |
|------------|---------|----------|---------------------|-------|
| Python 3 | PSF License | No (system) | Yes | Permissive |
| GTK 4 | LGPL-2.1-or-later | No (system) | Yes | Weak copyleft |
| Libadwaita | LGPL-2.1-or-later | No (system) | Yes | Weak copyleft |
| PyGObject | LGPL-2.1-or-later | No (system) | Yes | Python bindings for GTK |
| GStreamer | LGPL-2.1-or-later | No (system) | Yes | Weak copyleft |
| Flatpak | LGPL-2.1-or-later | No (system) | Yes | Invoked via CLI only |
| PolicyKit | LGPL-2.0-or-later | No (system) | Yes | Invoked via CLI only |
| Timeshift | GPL-3.0 | No (system) | Yes | Same license family |
| UFW | GPL-3.0 | No (system) | Yes | Same license family |
| ubuntu-drivers | GPL-3.0 | No (system) | Yes | Same license family |
| power-profiles-daemon | GPL-3.0-or-later | No (system) | Yes | Same license family |
| systemd | LGPL-2.1-or-later | No (system) | Yes | Invoked via CLI only |
| Git | GPL-2.0 | No (system) | Yes | Invoked via CLI only |
| Wine | LGPL-2.1 | No (optional) | Yes | Invoked via CLI only |
| Bottles | GPL-3.0 | No (Flatpak) | Yes | Same license family |

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

## 4. Auto-Update Feature Compliance (New in v1.1.0)

The auto-update feature downloads `.deb` packages from the project's own GitHub Releases:

| Concern | Status | Details |
|---------|--------|---------|
| Source of downloads | PASS | GitHub Releases for `Naftaliro/first-steps` only |
| Third-party binaries | PASS | No third-party binaries fetched |
| User consent | PASS | Update requires explicit user confirmation via dialog |
| Source availability | PASS | All versions remain publicly available on GitHub |
| License consistency | PASS | All releases use the same GPL-3.0-or-later license |

**No additional licensing concerns from the auto-update feature.**

## 5. Distribution Compliance Checklist

| Requirement | Status | Details |
|-------------|--------|---------|
| LICENSE file present | PASS | Full GPL-3.0 text from gnu.org |
| SPDX identifiers in all source files | PASS | Verified across all 23 source files |
| Copyright notices present | PASS | "Copyright 2026 Naftali" |
| NOTICE file for third-party attribution | PASS | Lists all runtime dependencies |
| No proprietary code included | PASS | 100% original code |
| No bundled third-party code | PASS | All dependencies are system packages |
| AppStream metadata license | PASS | CC0-1.0 for metadata, GPL-3.0-or-later for project |
| Desktop entry compliant | PASS | Follows freedesktop.org specification |
| Polkit policy file | PASS | Standard freedesktop PolicyKit format |
| Debian copyright file in .deb | PASS | DEP-5 format |
| CONTRIBUTING.md | PASS | License contribution terms documented |

## 6. Files Inventory

```
15  Python source files (.py)
 4  Shell scripts (.sh, helper)
 1  Desktop entry (.desktop)
 1  Polkit policy (.policy)
 1  AppStream metainfo (.metainfo.xml)
 1  SVG icon (.svg)
 1  LICENSE (GPL-3.0 full text)
 1  NOTICE (dependency attribution)
 1  CONTRIBUTING.md
 1  README.md
 1  LICENSING-AUDIT.md
 1  .gitignore
---
29  Total tracked files
```

## 7. Recommendations

1. **No action required** — the project is fully compliant with GPL-3.0-or-later licensing requirements.
2. If the project is ever distributed as a Flatpak, ensure the runtime manifest references the correct license metadata.
3. If third-party icons or assets are added in the future, their licenses must be documented in the NOTICE file and verified for GPL compatibility.
4. When creating new releases, ensure the `.deb` package includes the updated `copyright` file.

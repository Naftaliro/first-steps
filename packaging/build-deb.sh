#!/bin/bash
# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright 2026 Naftali
#
# build-deb.sh — Build the .deb package from the current source tree.
#
# Usage: ./packaging/build-deb.sh
#
# Output: first-steps_<version>-1_all.deb in the project root

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
VERSION=$(python3 -c "import sys; sys.path.insert(0,'$PROJECT_DIR'); from first_steps import __version__; print(__version__)")
PKG_NAME="first-steps_${VERSION}-1_all"
BUILD_DIR="${SCRIPT_DIR}/deb/${PKG_NAME}"

echo "Building first-steps ${VERSION} .deb package..."

# Clean previous build
rm -rf "$BUILD_DIR"

# Create directory structure
mkdir -p "${BUILD_DIR}"/{DEBIAN,usr/bin,usr/lib/first-steps/first_steps/{pages,helpers},usr/share/{applications,icons/hicolor/scalable/apps,polkit-1/actions,metainfo,doc/first-steps}}

# ── Generate DEBIAN/control ──────────────────────────────────────────
cat > "${BUILD_DIR}/DEBIAN/control" << EOF
Package: first-steps
Version: ${VERSION}-1
Section: admin
Priority: optional
Architecture: all
Depends: python3 (>= 3.10), python3-gi, gir1.2-gtk-4.0, gir1.2-adw-1, flatpak, policykit-1
Recommends: ubuntu-drivers-common, timeshift, ufw
Maintainer: Naftali <https://github.com/Naftaliro/first-steps>
Homepage: https://github.com/Naftaliro/first-steps
Description: GTK4 + LibAdwaita onboarding wizard
 First Steps is a graphical setup wizard that helps new users configure
 their system after installation. It handles codecs, Flatpak, drivers,
 Windows app compatibility, backups, power management, and more —
 all without touching a terminal.
EOF

# ── Generate DEBIAN/postinst ─────────────────────────────────────────
cat > "${BUILD_DIR}/DEBIAN/postinst" << 'EOF'
#!/bin/bash
set -e
if command -v gtk-update-icon-cache &>/dev/null; then
    gtk-update-icon-cache -f -t /usr/share/icons/hicolor 2>/dev/null || true
fi
if command -v update-desktop-database &>/dev/null; then
    update-desktop-database /usr/share/applications 2>/dev/null || true
fi
EOF

# ── Generate DEBIAN/postrm ──────────────────────────────────────────
cat > "${BUILD_DIR}/DEBIAN/postrm" << 'EOF'
#!/bin/bash
set -e
if [ "$1" = "remove" ] || [ "$1" = "purge" ]; then
    if command -v gtk-update-icon-cache &>/dev/null; then
        gtk-update-icon-cache -f -t /usr/share/icons/hicolor 2>/dev/null || true
    fi
fi
EOF

# ── Generate copyright ──────────────────────────────────────────────
cat > "${BUILD_DIR}/usr/share/doc/first-steps/copyright" << EOF
Format: https://www.debian.org/doc/packaging-manuals/copyright-format/1.0/
Upstream-Name: First Steps
Upstream-Contact: https://github.com/Naftaliro/first-steps
Source: https://github.com/Naftaliro/first-steps

Files: *
Copyright: 2026 Naftali
License: GPL-3.0-or-later

License: GPL-3.0-or-later
 This program is free software: you can redistribute it and/or modify
 it under the terms of the GNU General Public License as published by
 the Free Software Foundation, either version 3 of the License, or
 (at your option) any later version.
 .
 This program is distributed in the hope that it will be useful,
 but WITHOUT ANY WARRANTY; without even the implied warranty of
 MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
 GNU General Public License for more details.
 .
 On Debian systems, the complete text of the GNU General Public License
 version 3 can be found in /usr/share/common-licenses/GPL-3.
EOF

# ── Generate entry point ────────────────────────────────────────────
cat > "${BUILD_DIR}/usr/bin/first-steps" << 'EOF'
#!/usr/bin/python3
# SPDX-License-Identifier: GPL-3.0-or-later
import sys
sys.path.insert(0, "/usr/lib/first-steps")
from first_steps.app import FirstStepsApp
sys.exit(FirstStepsApp().run(sys.argv))
EOF

# ── Copy application files ──────────────────────────────────────────
cp "${PROJECT_DIR}/first_steps/__init__.py" "${BUILD_DIR}/usr/lib/first-steps/first_steps/"
cp "${PROJECT_DIR}/first_steps/app.py" "${BUILD_DIR}/usr/lib/first-steps/first_steps/"
cp "${PROJECT_DIR}/first_steps/updater.py" "${BUILD_DIR}/usr/lib/first-steps/first_steps/"
cp "${PROJECT_DIR}/first_steps/helpers/__init__.py" "${BUILD_DIR}/usr/lib/first-steps/first_steps/helpers/"
cp "${PROJECT_DIR}/first_steps/pages/"*.py "${BUILD_DIR}/usr/lib/first-steps/first_steps/pages/"
cp "${PROJECT_DIR}/scripts/first-steps-helper" "${BUILD_DIR}/usr/lib/first-steps/"

# Copy data files
cp "${PROJECT_DIR}/data/io.github.firststeps.desktop" "${BUILD_DIR}/usr/share/applications/"
cp "${PROJECT_DIR}/data/io.github.firststeps.policy" "${BUILD_DIR}/usr/share/polkit-1/actions/"
cp "${PROJECT_DIR}/data/io.github.firststeps.metainfo.xml" "${BUILD_DIR}/usr/share/metainfo/"
cp "${PROJECT_DIR}/data/icons/hicolor/scalable/apps/io.github.firststeps.svg" "${BUILD_DIR}/usr/share/icons/hicolor/scalable/apps/"

# ── Set permissions ─────────────────────────────────────────────────
chmod 755 "${BUILD_DIR}/DEBIAN/postinst" "${BUILD_DIR}/DEBIAN/postrm"
chmod 755 "${BUILD_DIR}/usr/bin/first-steps"
chmod 755 "${BUILD_DIR}/usr/lib/first-steps/first-steps-helper"
find "${BUILD_DIR}/usr" -type f -name "*.py" -exec chmod 644 {} \;
find "${BUILD_DIR}/usr/share" -type f -exec chmod 644 {} \;

# ── Build ────────────────────────────────────────────────────────────
dpkg-deb --build --root-owner-group "${BUILD_DIR}"
cp "${BUILD_DIR}.deb" "${PROJECT_DIR}/"

echo ""
echo "Built: ${PROJECT_DIR}/${PKG_NAME}.deb"
echo "Size: $(du -h "${PROJECT_DIR}/${PKG_NAME}.deb" | cut -f1)"

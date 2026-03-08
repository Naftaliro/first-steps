#!/bin/bash
# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright 2026 First Steps Contributors
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

# Copy DEBIAN control files
cp "${SCRIPT_DIR}/deb/first-steps_1.0.0-1_all/DEBIAN/control" "${BUILD_DIR}/DEBIAN/"
cp "${SCRIPT_DIR}/deb/first-steps_1.0.0-1_all/DEBIAN/postinst" "${BUILD_DIR}/DEBIAN/"
cp "${SCRIPT_DIR}/deb/first-steps_1.0.0-1_all/DEBIAN/postrm" "${BUILD_DIR}/DEBIAN/"

# Update version in control file
sed -i "s/^Version:.*/Version: ${VERSION}-1/" "${BUILD_DIR}/DEBIAN/control"

# Copy application files
cp "${PROJECT_DIR}/first_steps/__init__.py" "${BUILD_DIR}/usr/lib/first-steps/first_steps/"
cp "${PROJECT_DIR}/first_steps/app.py" "${BUILD_DIR}/usr/lib/first-steps/first_steps/"
cp "${PROJECT_DIR}/first_steps/helpers/__init__.py" "${BUILD_DIR}/usr/lib/first-steps/first_steps/helpers/"
cp "${PROJECT_DIR}/first_steps/pages/"*.py "${BUILD_DIR}/usr/lib/first-steps/first_steps/pages/"
cp "${PROJECT_DIR}/scripts/first-steps-helper" "${BUILD_DIR}/usr/lib/first-steps/"

# Copy entry point
cp "${SCRIPT_DIR}/deb/first-steps_1.0.0-1_all/usr/bin/first-steps" "${BUILD_DIR}/usr/bin/"

# Copy data files
cp "${PROJECT_DIR}/data/io.github.firststeps.desktop" "${BUILD_DIR}/usr/share/applications/"
cp "${PROJECT_DIR}/data/io.github.firststeps.policy" "${BUILD_DIR}/usr/share/polkit-1/actions/"
cp "${PROJECT_DIR}/data/io.github.firststeps.metainfo.xml" "${BUILD_DIR}/usr/share/metainfo/"
cp "${PROJECT_DIR}/data/icons/hicolor/scalable/apps/io.github.firststeps.svg" "${BUILD_DIR}/usr/share/icons/hicolor/scalable/apps/"
cp "${SCRIPT_DIR}/deb/first-steps_1.0.0-1_all/usr/share/doc/first-steps/copyright" "${BUILD_DIR}/usr/share/doc/first-steps/"

# Set permissions
chmod 755 "${BUILD_DIR}/DEBIAN/postinst" "${BUILD_DIR}/DEBIAN/postrm"
chmod 755 "${BUILD_DIR}/usr/bin/first-steps"
chmod 755 "${BUILD_DIR}/usr/lib/first-steps/first-steps-helper"
find "${BUILD_DIR}/usr" -type f -name "*.py" -exec chmod 644 {} \;
find "${BUILD_DIR}/usr/share" -type f -exec chmod 644 {} \;

# Build
dpkg-deb --build --root-owner-group "${BUILD_DIR}"
cp "${BUILD_DIR}.deb" "${PROJECT_DIR}/"

echo ""
echo "Built: ${PROJECT_DIR}/${PKG_NAME}.deb"
echo "Size: $(du -h "${PROJECT_DIR}/${PKG_NAME}.deb" | cut -f1)"

#!/bin/bash
# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright 2026 Naftali Rosen
#
# install.sh — Install First Steps onboarding wizard system-wide.
#
# Usage:
#   sudo ./install.sh          # Install
#   sudo ./install.sh remove   # Uninstall

set -euo pipefail

PREFIX="${PREFIX:-/usr}"
BINDIR="${PREFIX}/bin"
LIBDIR="${PREFIX}/lib/first-steps"
DATADIR="${PREFIX}/share"
POLKITDIR="${DATADIR}/polkit-1/actions"
DESKTOPDIR="${DATADIR}/applications"
ICONDIR="${DATADIR}/icons"

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# ── Colors ───────────────────────────────────────────────────────────
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

info()  { echo -e "${BLUE}[INFO]${NC}  $*"; }
ok()    { echo -e "${GREEN}[OK]${NC}    $*"; }
warn()  { echo -e "${YELLOW}[WARN]${NC}  $*"; }
error() { echo -e "${RED}[ERROR]${NC} $*" >&2; }

# ── Check root ───────────────────────────────────────────────────────
if [ "$(id -u)" -ne 0 ]; then
    error "This script must be run as root (use sudo)."
    exit 1
fi

# ── Uninstall ────────────────────────────────────────────────────────
do_remove() {
    info "Removing First Steps..."
    rm -f  "${BINDIR}/first-steps"
    rm -rf "${LIBDIR}"
    rm -f  "${POLKITDIR}/io.github.firststeps.policy"
    rm -f  "${DESKTOPDIR}/io.github.firststeps.desktop"
    rm -f  "${ICONDIR}/hicolor/scalable/apps/io.github.firststeps.svg"
    gtk-update-icon-cache -f -t "${ICONDIR}/hicolor" 2>/dev/null || true
    ok "First Steps has been removed."
}

# ── Install ──────────────────────────────────────────────────────────
do_install() {
    info "Installing First Steps..."

    # Check dependencies
    info "Checking dependencies..."
    local missing=()
    python3 -c "import gi; gi.require_version('Gtk', '4.0'); gi.require_version('Adw', '1')" 2>/dev/null || {
        missing+=("gir1.2-adw-1" "python3-gi")
    }
    command -v flatpak &>/dev/null || missing+=("flatpak")

    if [ ${#missing[@]} -gt 0 ]; then
        warn "Installing missing dependencies: ${missing[*]}"
        apt-get update -qq
        apt-get install -y "${missing[@]}"
    fi

    # Install Python package
    info "Installing application files..."
    mkdir -p "${LIBDIR}"
    cp -r "${SCRIPT_DIR}/first_steps" "${LIBDIR}/"

    # Install entry point
    mkdir -p "${BINDIR}"
    cat > "${BINDIR}/first-steps" << 'ENTRY'
#!/usr/bin/env python3
import sys
import os
sys.path.insert(0, "/usr/lib/first-steps")
from first_steps.app import FirstStepsApp
sys.exit(FirstStepsApp().run(sys.argv))
ENTRY
    chmod +x "${BINDIR}/first-steps"

    # Install helper script
    install -m 755 "${SCRIPT_DIR}/scripts/first-steps-helper" "${LIBDIR}/first-steps-helper"

    # Install polkit policy
    mkdir -p "${POLKITDIR}"
    install -m 644 "${SCRIPT_DIR}/data/io.github.firststeps.policy" "${POLKITDIR}/"

    # Install desktop entry
    mkdir -p "${DESKTOPDIR}"
    install -m 644 "${SCRIPT_DIR}/data/io.github.firststeps.desktop" "${DESKTOPDIR}/"

    # Install icon
    mkdir -p "${ICONDIR}/hicolor/scalable/apps"
    install -m 644 "${SCRIPT_DIR}/data/icons/hicolor/scalable/apps/io.github.firststeps.svg" \
        "${ICONDIR}/hicolor/scalable/apps/"
    gtk-update-icon-cache -f -t "${ICONDIR}/hicolor" 2>/dev/null || true

    ok "First Steps installed successfully!"
    echo ""
    info "Run 'first-steps' or find it in your application menu."
}

# ── Main ─────────────────────────────────────────────────────────────
case "${1:-install}" in
    remove|uninstall)
        do_remove
        ;;
    install|"")
        do_install
        ;;
    *)
        echo "Usage: $0 [install|remove]"
        exit 1
        ;;
esac

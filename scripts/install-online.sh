#!/bin/bash
# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright 2026 First Steps Contributors
#
# One-click online installer for First Steps
# Usage: curl -fsSL https://raw.githubusercontent.com/Naftaliro/first-steps/main/scripts/install-online.sh | sudo bash
#
# This script:
#   1. Installs required dependencies (python3-gi, gir1.2-adw-1, flatpak, etc.)
#   2. Downloads the latest .deb from GitHub Releases
#   3. Installs the .deb package
#   4. Cleans up

set -euo pipefail

# ── Colors ───────────────────────────────────────────────────────────
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
BOLD='\033[1m'
NC='\033[0m'

info()    { echo -e "${BLUE}[INFO]${NC}    $*"; }
ok()      { echo -e "${GREEN}[OK]${NC}      $*"; }
warn()    { echo -e "${YELLOW}[WARN]${NC}    $*"; }
error()   { echo -e "${RED}[ERROR]${NC}   $*" >&2; }
header()  { echo -e "\n${BOLD}$*${NC}"; }

REPO="Naftaliro/first-steps"
TMP_DIR=$(mktemp -d)

cleanup() {
    rm -rf "$TMP_DIR"
}
trap cleanup EXIT

# ── Banner ───────────────────────────────────────────────────────────
echo ""
echo -e "${BOLD}╔══════════════════════════════════════════════════════════╗${NC}"
echo -e "${BOLD}║                                                          ║${NC}"
echo -e "${BOLD}║     ${BLUE}First Steps${NC}${BOLD} — Onboarding Wizard Installer          ║${NC}"
echo -e "${BOLD}║                                                          ║${NC}"
echo -e "${BOLD}╚══════════════════════════════════════════════════════════╝${NC}"
echo ""

# ── Root check ───────────────────────────────────────────────────────
if [ "$(id -u)" -ne 0 ]; then
    error "This installer must be run as root."
    echo ""
    echo "  Run with:  curl -fsSL https://raw.githubusercontent.com/${REPO}/main/scripts/install-online.sh | sudo bash"
    echo ""
    exit 1
fi

# ── OS check ─────────────────────────────────────────────────────────
header "Checking system compatibility..."

if [ -f /etc/os-release ]; then
    . /etc/os-release
    info "Detected: ${PRETTY_NAME:-Unknown}"
else
    warn "Could not detect OS. Proceeding anyway..."
fi

# Check for apt
if ! command -v apt-get &>/dev/null; then
    error "This installer requires apt-get (Debian/Ubuntu-based systems)."
    exit 1
fi
ok "System is apt-based"

# ── Dependencies ─────────────────────────────────────────────────────
header "Installing dependencies..."

DEPS=(
    python3
    python3-gi
    gir1.2-gtk-4.0
    gir1.2-adw-1
    flatpak
    policykit-1
    curl
)

info "Required packages: ${DEPS[*]}"
apt-get update -qq
DEBIAN_FRONTEND=noninteractive apt-get install -y "${DEPS[@]}" 2>&1 | tail -1
ok "Dependencies installed"

# ── Download ─────────────────────────────────────────────────────────
header "Downloading First Steps..."

# Dynamically find the latest .deb from GitHub Releases API
DEB_URL=""
if command -v curl &>/dev/null; then
    RELEASE_JSON=$(curl -fsSL "https://api.github.com/repos/${REPO}/releases/latest" 2>/dev/null || echo "")
    if [ -n "$RELEASE_JSON" ]; then
        # Extract .deb download URL from JSON (portable grep approach)
        DEB_URL=$(echo "$RELEASE_JSON" | grep -o '"browser_download_url"[[:space:]]*:[[:space:]]*"[^"]*\.deb"' | head -1 | grep -o 'https://[^"]*')
    fi
fi

# Fallback to known latest URL pattern
if [ -z "$DEB_URL" ]; then
    DEB_URL="https://github.com/${REPO}/releases/latest/download/first-steps_1.1.0-1_all.deb"
    warn "Could not query GitHub API, using fallback URL"
fi

DEB_FILE="${TMP_DIR}/first-steps.deb"
info "Downloading from: ${DEB_URL}"

if curl -fsSL -o "${DEB_FILE}" "${DEB_URL}" 2>/dev/null; then
    ok "Downloaded .deb package"

    # ── Install .deb ─────────────────────────────────────────────────
    header "Installing First Steps..."
    dpkg -i "${DEB_FILE}" 2>&1
    # Fix any missing dependencies
    apt-get install -f -y 2>&1 | tail -1
    ok "First Steps installed via .deb package"
else
    warn "Could not download .deb from GitHub Releases."
    info "Falling back to install from source..."

    # Clone and install from source
    if ! command -v git &>/dev/null; then
        apt-get install -y git
    fi

    git clone "https://github.com/${REPO}.git" "${TMP_DIR}/first-steps" 2>&1 | tail -1
    cd "${TMP_DIR}/first-steps"
    bash install.sh
    ok "First Steps installed from source"
fi

# ── Done ─────────────────────────────────────────────────────────────
echo ""
echo -e "${GREEN}${BOLD}╔══════════════════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}${BOLD}║                                                          ║${NC}"
echo -e "${GREEN}${BOLD}║     First Steps installed successfully!                   ║${NC}"
echo -e "${GREEN}${BOLD}║                                                          ║${NC}"
echo -e "${GREEN}${BOLD}║     Launch from your app menu or run:  first-steps        ║${NC}"
echo -e "${GREEN}${BOLD}║                                                          ║${NC}"
echo -e "${GREEN}${BOLD}║     To uninstall:  sudo apt remove first-steps            ║${NC}"
echo -e "${GREEN}${BOLD}║                                                          ║${NC}"
echo -e "${GREEN}${BOLD}╚══════════════════════════════════════════════════════════╝${NC}"
echo ""

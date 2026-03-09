#!/bin/bash
# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright 2026 Naftali Rosen
#
# One-click online installer for First Steps
# Usage: curl -fsSL https://raw.githubusercontent.com/Naftaliro/first-steps/main/scripts/install-online.sh | sudo bash
#
# Security:
#   - Downloads .deb from GitHub Releases only
#   - Verifies SHA-256 checksum against published SHA256SUMS file
#   - Falls back to source install (with git clone over HTTPS) if .deb is unavailable
#
# This script:
#   1. Verifies system compatibility
#   2. Installs required dependencies
#   3. Downloads the latest .deb from GitHub Releases
#   4. Verifies its SHA-256 checksum
#   5. Installs the .deb package
#   6. Cleans up

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
    # shellcheck disable=SC1091
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
    ca-certificates
)

info "Required packages: ${DEPS[*]}"
apt-get update -qq
DEBIAN_FRONTEND=noninteractive apt-get install -y "${DEPS[@]}" 2>&1 | tail -1
ok "Dependencies installed"

# ── Download ─────────────────────────────────────────────────────────
header "Downloading First Steps..."

install_from_source() {
    info "Installing from source..."
    if ! command -v git &>/dev/null; then
        apt-get install -y git
    fi
    git clone "https://github.com/${REPO}.git" "${TMP_DIR}/first-steps" 2>&1 | tail -1
    cd "${TMP_DIR}/first-steps"
    bash install.sh
    ok "First Steps installed from source"
}

# Query GitHub Releases API for the latest release
DEB_URL=""
SUMS_URL=""
RELEASE_JSON=$(curl -fsSL "https://api.github.com/repos/${REPO}/releases/latest" 2>/dev/null || echo "")

if [ -n "$RELEASE_JSON" ]; then
    # Extract .deb download URL
    DEB_URL=$(echo "$RELEASE_JSON" | grep -o '"browser_download_url"[[:space:]]*:[[:space:]]*"[^"]*\.deb"' | head -1 | grep -o 'https://[^"]*' || echo "")
    # Extract SHA256SUMS download URL
    SUMS_URL=$(echo "$RELEASE_JSON" | grep -o '"browser_download_url"[[:space:]]*:[[:space:]]*"[^"]*SHA256SUMS"' | head -1 | grep -o 'https://[^"]*' || echo "")
fi

if [ -z "$DEB_URL" ]; then
    warn "Could not find .deb in latest GitHub Release."
    install_from_source
else
    DEB_FILE="${TMP_DIR}/first-steps.deb"
    info "Downloading from: ${DEB_URL}"

    if ! curl -fsSL -o "${DEB_FILE}" "${DEB_URL}" 2>/dev/null; then
        warn "Download failed."
        install_from_source
    else
        ok "Downloaded .deb package"

        # ── Checksum verification ────────────────────────────────────
        header "Verifying integrity..."

        if [ -n "$SUMS_URL" ]; then
            SUMS_FILE="${TMP_DIR}/SHA256SUMS"
            if curl -fsSL -o "${SUMS_FILE}" "${SUMS_URL}" 2>/dev/null; then
                # Extract expected hash for the .deb filename
                DEB_BASENAME=$(basename "$DEB_URL")
                EXPECTED_HASH=$(grep "${DEB_BASENAME}" "${SUMS_FILE}" | awk '{print $1}')

                if [ -n "$EXPECTED_HASH" ]; then
                    ACTUAL_HASH=$(sha256sum "${DEB_FILE}" | awk '{print $1}')
                    if [ "$EXPECTED_HASH" = "$ACTUAL_HASH" ]; then
                        ok "SHA-256 checksum verified: ${ACTUAL_HASH:0:16}..."
                    else
                        error "SHA-256 checksum mismatch!"
                        error "  Expected: ${EXPECTED_HASH}"
                        error "  Actual:   ${ACTUAL_HASH}"
                        error ""
                        error "The downloaded file may be corrupted or tampered with."
                        error "Aborting installation for security. Try again or install from source:"
                        error "  git clone https://github.com/${REPO}.git && cd first-steps && sudo ./install.sh"
                        exit 1
                    fi
                else
                    warn "Could not find checksum for ${DEB_BASENAME} in SHA256SUMS"
                    warn "Proceeding without checksum verification"
                fi
            else
                warn "Could not download SHA256SUMS file"
                warn "Proceeding without checksum verification"
            fi
        else
            warn "No SHA256SUMS file found in release"
            warn "Proceeding without checksum verification"
        fi

        # ── Install .deb ─────────────────────────────────────────────
        header "Installing First Steps..."
        dpkg -i "${DEB_FILE}" 2>&1
        # Fix any missing dependencies
        apt-get install -f -y 2>&1 | tail -1
        ok "First Steps installed via .deb package"
    fi
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

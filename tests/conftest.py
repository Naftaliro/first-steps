# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright 2026 Naftali Rosen
"""Pytest configuration and shared fixtures."""

import sys
import os

# Add project root to path so tests can import first_steps
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

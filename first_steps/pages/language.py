# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright 2026 Naftali Rosen
"""Localization page — language packs, input methods, and spell-check."""

import os
import subprocess
import tempfile
import threading

import gi

gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")

from gi.repository import Adw, GLib, Gtk

from first_steps.pages import BasePage


def _detect_locale() -> str:
    """Detect the current system locale."""
    for var in ("LANG", "LC_ALL", "LANGUAGE"):
        val = os.environ.get(var, "")
        if val:
            return val.split(".")[0].split("_")[0]
    return "en"


class LanguagePage(BasePage):
    PAGE_TAG = "language"
    PAGE_TITLE = "Language"
    PAGE_ICON = "preferences-desktop-locale-symbolic"

    def build_ui(self) -> None:
        self.add_status_page(
            "preferences-desktop-locale-symbolic",
            "Language & Input Methods",
            "Install language packs, input methods, and spell-check "
            "dictionaries for your preferred languages."
        )

        # ── Detected locale ──────────────────────────────────────────
        locale = _detect_locale()
        info_group = self.add_preferences_group(
            "Current Language",
            f"Detected system language: {os.environ.get('LANG', 'Not set')}"
        )

        # ── Language packs ───────────────────────────────────────────
        lang_group = self.add_preferences_group(
            "Language Support Packs",
            "Install full language support including translations and fonts:"
        )

        self._lang_packs = {}
        languages = [
            ("en", "English", "language-pack-en language-pack-gnome-en"),
            ("es", "Spanish (Espa\u00f1ol)", "language-pack-es language-pack-gnome-es"),
            ("fr", "French (Fran\u00e7ais)", "language-pack-fr language-pack-gnome-fr"),
            ("de", "German (Deutsch)", "language-pack-de language-pack-gnome-de"),
            ("pt", "Portuguese (Portugu\u00eas)", "language-pack-pt language-pack-gnome-pt"),
            ("zh", "Chinese (\u4e2d\u6587)", "language-pack-zh-hans language-pack-gnome-zh-hans"),
            ("ja", "Japanese (\u65e5\u672c\u8a9e)", "language-pack-ja language-pack-gnome-ja"),
            ("ko", "Korean (\ud55c\uad6d\uc5b4)", "language-pack-ko language-pack-gnome-ko"),
            ("ar", "Arabic (\u0627\u0644\u0639\u0631\u0628\u064a\u0629)", "language-pack-ar language-pack-gnome-ar"),
            ("ru", "Russian (\u0420\u0443\u0441\u0441\u043a\u0438\u0439)", "language-pack-ru language-pack-gnome-ru"),
            ("hi", "Hindi (\u0939\u093f\u0928\u094d\u0926\u0940)", "language-pack-hi language-pack-gnome-hi"),
            ("it", "Italian (Italiano)", "language-pack-it language-pack-gnome-it"),
        ]

        for code, name, pkgs in languages:
            active = code == locale
            row, check = self.add_action_row_with_check(
                lang_group, name, f"Packages: {pkgs}", active=active
            )
            self._lang_packs[pkgs] = check

        install_lang_btn = Gtk.Button(label="Install Selected Language Packs")
        install_lang_btn.add_css_class("suggested-action")
        install_lang_btn.set_halign(Gtk.Align.CENTER)
        install_lang_btn.connect("clicked", self._on_install_langs)
        self._outer_box.append(install_lang_btn)

        # ── Input methods ────────────────────────────────────────────
        input_group = self.add_preferences_group(
            "Input Methods",
            "Install input method frameworks for CJK and other complex scripts:"
        )

        self._input_methods = {}
        methods = [
            ("ibus", "IBus", "Intelligent Input Bus \u2014 default GNOME input framework",
             "ibus ibus-gtk3 ibus-gtk4"),
            ("fcitx5", "Fcitx 5", "Flexible input method framework with wide language support",
             "fcitx5 fcitx5-gtk3 fcitx5-gtk4"),
            ("ibus-pinyin", "IBus Pinyin", "Chinese Pinyin input for IBus",
             "ibus-pinyin"),
            ("ibus-anthy", "IBus Anthy", "Japanese input for IBus",
             "ibus-anthy"),
            ("ibus-hangul", "IBus Hangul", "Korean input for IBus",
             "ibus-hangul"),
            ("ibus-m17n", "IBus M17n", "Multilingual input for many languages",
             "ibus-m17n"),
        ]

        for key, name, desc, pkgs in methods:
            row, check = self.add_action_row_with_check(
                input_group, name, desc
            )
            self._input_methods[pkgs] = check

        install_input_btn = Gtk.Button(label="Install Selected Input Methods")
        install_input_btn.add_css_class("suggested-action")
        install_input_btn.set_halign(Gtk.Align.CENTER)
        install_input_btn.connect("clicked", self._on_install_input)
        self._outer_box.append(install_input_btn)

        # ── Spell-check dictionaries ─────────────────────────────────
        spell_group = self.add_preferences_group(
            "Spell-Check Dictionaries",
            "Install dictionaries for LibreOffice and other applications:"
        )

        self._spell_dicts = {}
        dicts = [
            ("hunspell-en-us", "English (US)"),
            ("hunspell-en-gb", "English (UK)"),
            ("hunspell-es", "Spanish"),
            ("hunspell-fr", "French"),
            ("hunspell-de-de", "German"),
            ("hunspell-pt-br", "Portuguese (Brazil)"),
            ("hunspell-it", "Italian"),
            ("hunspell-ru", "Russian"),
        ]

        for pkg, name in dicts:
            row, check = self.add_action_row_with_check(
                spell_group, name, f"Package: {pkg}"
            )
            self._spell_dicts[pkg] = check

        install_spell_btn = Gtk.Button(label="Install Selected Dictionaries")
        install_spell_btn.add_css_class("suggested-action")
        install_spell_btn.set_halign(Gtk.Align.CENTER)
        install_spell_btn.connect("clicked", self._on_install_spell)
        self._outer_box.append(install_spell_btn)

        # ── Fonts ────────────────────────────────────────────────────
        fonts_group = self.add_preferences_group(
            "Additional Fonts",
            "Install font families for better international text rendering:"
        )

        self._fonts = {}
        font_pkgs = [
            ("fonts-noto", "Google Noto Fonts",
             "Comprehensive Unicode font family covering all scripts"),
            ("fonts-noto-cjk", "Noto CJK Fonts",
             "Chinese, Japanese, and Korean font support"),
            ("fonts-noto-color-emoji", "Noto Color Emoji",
             "Full-color emoji font"),
            ("fonts-firacode", "Fira Code",
             "Monospaced font with programming ligatures"),
            ("fonts-cascadia-code", "Cascadia Code",
             "Microsoft's monospaced font for developers"),
            ("fonts-liberation", "Liberation Fonts",
             "Metrically compatible with Arial, Times, and Courier"),
        ]

        for pkg, name, desc in font_pkgs:
            row, check = self.add_action_row_with_check(
                fonts_group, name, desc
            )
            self._fonts[pkg] = check

        install_fonts_btn = Gtk.Button(label="Install Selected Fonts")
        install_fonts_btn.add_css_class("suggested-action")
        install_fonts_btn.set_halign(Gtk.Align.CENTER)
        install_fonts_btn.connect("clicked", self._on_install_fonts)
        self._outer_box.append(install_fonts_btn)

        self.add_navigation_buttons(back_tag="development", next_tag="extras")

    def _install_apt_packages(self, packages: list[str], category: str) -> None:
        """Helper to install apt packages via pkexec."""
        if not packages:
            self.show_toast(f"No {category} selected")
            return

        script = (
            "#!/bin/bash\nset -e\n"
            "export DEBIAN_FRONTEND=noninteractive\n"
            f"apt-get install -y {' '.join(packages)}\n"
        )

        with tempfile.NamedTemporaryFile(mode="w", suffix=".sh", delete=False) as f:
            f.write(script)
            tmp_path = f.name
        os.chmod(tmp_path, 0o755)

        def _done(success, output):
            try:
                os.unlink(tmp_path)
            except OSError:
                pass
            if success:
                self.show_toast(f"Installed {len(packages)} {category}")
            else:
                self.show_error_dialog("Installation Failed", output[:500])

        self.run_privileged(
            [tmp_path],
            f"Installed {category}: {', '.join(packages)}",
            _done
        )

    def _on_install_langs(self, btn) -> None:
        """Install selected language packs."""
        pkgs = []
        for pkg_str, check in self._lang_packs.items():
            if check.get_active():
                pkgs.extend(pkg_str.split())
        self._install_apt_packages(pkgs, "language packs")

    def _on_install_input(self, btn) -> None:
        """Install selected input methods."""
        pkgs = []
        for pkg_str, check in self._input_methods.items():
            if check.get_active():
                pkgs.extend(pkg_str.split())
        self._install_apt_packages(pkgs, "input methods")

    def _on_install_spell(self, btn) -> None:
        """Install selected spell-check dictionaries."""
        pkgs = [
            pkg for pkg, check in self._spell_dicts.items()
            if check.get_active()
        ]
        self._install_apt_packages(pkgs, "dictionaries")

    def _on_install_fonts(self, btn) -> None:
        """Install selected font packages."""
        pkgs = [
            pkg for pkg, check in self._fonts.items()
            if check.get_active()
        ]
        self._install_apt_packages(pkgs, "fonts")

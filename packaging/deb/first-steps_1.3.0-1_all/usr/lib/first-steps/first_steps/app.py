# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright 2026 Naftali Rosen
"""Main application class — window, sidebar navigation, and page management."""

import gi

gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")

import subprocess
import sys

from gi.repository import Adw, Gdk, Gio, GLib, Gtk

from first_steps import __app_id__, __version__
from first_steps.updater import UpdateChecker
from first_steps.pages.welcome import WelcomePage
from first_steps.pages.codecs import CodecsPage
from first_steps.pages.flatpak import FlatpakPage
from first_steps.pages.drivers import DriversPage
from first_steps.pages.bottles import BottlesPage
from first_steps.pages.timeshift import TimeshiftPage
from first_steps.pages.power import PowerPage
from first_steps.pages.firewall import FirewallPage
from first_steps.pages.network import NetworkPage
from first_steps.pages.privacy import PrivacyPage
from first_steps.pages.development import DevelopmentPage
from first_steps.pages.language import LanguagePage
from first_steps.pages.extras import ExtrasPage
from first_steps.pages.summary import SummaryPage


# ── Page registry ────────────────────────────────────────────────────
PAGE_REGISTRY = [
    ("welcome",     "go-home-symbolic",                "Welcome",         WelcomePage),
    ("codecs",      "media-playback-start-symbolic",   "Codecs & Media",  CodecsPage),
    ("flatpak",     "system-software-install-symbolic", "Flatpak & Apps", FlatpakPage),
    ("drivers",     "preferences-system-symbolic",     "Drivers",         DriversPage),
    ("bottles",     "preferences-desktop-apps-symbolic","Windows Apps",    BottlesPage),
    ("timeshift",   "drive-harddisk-symbolic",         "Backup",          TimeshiftPage),
    ("power",       "battery-symbolic",                "Power",           PowerPage),
    ("firewall",    "security-high-symbolic",          "Firewall",        FirewallPage),
    ("network",     "network-wired-symbolic",          "Network",         NetworkPage),
    ("privacy",     "security-medium-symbolic",        "Privacy",         PrivacyPage),
    ("development", "utilities-terminal-symbolic",     "Development",     DevelopmentPage),
    ("language",    "preferences-desktop-locale-symbolic", "Language",    LanguagePage),
    ("extras",      "applications-utilities-symbolic",  "Extras",         ExtrasPage),
    ("summary",     "emblem-ok-symbolic",              "Summary",         SummaryPage),
]


class FirstStepsApp(Adw.Application):
    """Top-level application object."""

    def __init__(self) -> None:
        super().__init__(
            application_id=__app_id__,
            flags=Gio.ApplicationFlags.FLAGS_NONE,
        )
        self.completed_actions: list[str] = []

        # Register actions
        about_action = Gio.SimpleAction.new("about", None)
        about_action.connect("activate", self._on_about)
        self.add_action(about_action)

    # ── activation ───────────────────────────────────────────────────
    def do_activate(self) -> None:  # noqa: D401
        win = self.props.active_window
        if not win:
            win = FirstStepsWindow(application=self)
            # Check for updates on first launch (non-blocking)
            updater = UpdateChecker(win)
            updater.check_async()
        win.present()

    def _on_about(self, action, param) -> None:
        about = Adw.AboutWindow(
            transient_for=self.props.active_window,
            application_name="First Steps",
            application_icon="io.github.firststeps",
            developer_name="Naftali Rosen",
            version=__version__,
            website="https://github.com/Naftaliro/first-steps",
            issue_url="https://github.com/Naftaliro/first-steps/issues",
            license_type=Gtk.License.GPL_3_0,
            copyright="Copyright 2026 Naftali Rosen",
            developers=["Naftali Rosen"],
        )
        about.add_link("Buy Me a Coffee \u2615", "https://buymeacoffee.com/naftali")
        about.present()


class FirstStepsWindow(Adw.ApplicationWindow):
    """Main window with sidebar navigation and stacked content pages."""

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        self.set_title("First Steps")
        self.set_default_size(1000, 720)
        self.set_size_request(760, 520)

        self._pages: dict[str, object] = {}
        self._sidebar_rows: dict[str, Gtk.ListBoxRow] = {}
        self._sidebar_checks: dict[str, Gtk.Image] = {}
        self._build_ui()
        self._setup_keyboard_shortcuts()

    # ── UI construction ──────────────────────────────────────────────
    def _build_ui(self) -> None:
        # ── Toast overlay wraps everything ───────────────────────────
        self._toast_overlay = Adw.ToastOverlay()

        # ── Navigation view (split pane) ─────────────────────────────
        self._split = Adw.NavigationSplitView()
        self._split.set_min_sidebar_width(240)
        self._split.set_max_sidebar_width(300)

        # ── Sidebar ──────────────────────────────────────────────────
        sidebar_page = Adw.NavigationPage.new(self._build_sidebar(), "Navigation")
        self._split.set_sidebar(sidebar_page)

        # ── Content stack ────────────────────────────────────────────
        self._stack = Gtk.Stack()
        self._stack.set_transition_type(Gtk.StackTransitionType.SLIDE_LEFT_RIGHT)
        self._stack.set_transition_duration(200)

        for tag, icon, title, PageClass in PAGE_REGISTRY:
            page_widget = PageClass(window=self)
            self._pages[tag] = page_widget
            self._stack.add_named(page_widget, tag)

        # Wrap content in a toolbar view with a header
        content_toolbar = Adw.ToolbarView()
        content_header = Adw.HeaderBar()

        # Dark/Light mode toggle button
        self._dark_toggle = Gtk.ToggleButton()
        self._dark_toggle.set_icon_name("weather-clear-night-symbolic")
        self._dark_toggle.set_tooltip_text("Toggle dark mode")
        self._dark_toggle.connect("toggled", self._on_dark_toggled)
        content_header.pack_end(self._dark_toggle)

        # Detect current color scheme
        style_mgr = Adw.StyleManager.get_default()
        if style_mgr.get_dark():
            self._dark_toggle.set_active(True)

        # Add About menu button
        menu_btn = Gtk.MenuButton()
        menu_btn.set_icon_name("open-menu-symbolic")
        menu = Gio.Menu()
        menu.append("About First Steps", "app.about")
        menu_btn.set_menu_model(menu)
        content_header.pack_end(menu_btn)

        self._content_title = Adw.WindowTitle.new("Welcome", "Let's get your system ready")
        content_header.set_title_widget(self._content_title)
        content_toolbar.add_top_bar(content_header)
        content_toolbar.set_content(self._stack)

        content_page = Adw.NavigationPage.new(content_toolbar, "Content")
        self._split.set_content(content_page)

        self._toast_overlay.set_child(self._split)
        self.set_content(self._toast_overlay)

        # Show welcome page initially
        self._stack.set_visible_child_name("welcome")
        self._sidebar_list.select_row(self._sidebar_list.get_row_at_index(0))

    def _build_sidebar(self) -> Gtk.Widget:
        """Build the sidebar with a list of navigation items."""
        toolbar = Adw.ToolbarView()

        header = Adw.HeaderBar()
        header.set_show_end_title_buttons(False)
        title = Adw.WindowTitle.new("First Steps", "Setup Wizard")
        header.set_title_widget(title)
        toolbar.add_top_bar(header)

        # Main vertical box to hold the list and the donation button
        sidebar_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)

        scrolled = Gtk.ScrolledWindow()
        scrolled.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        scrolled.set_vexpand(True)

        self._sidebar_list = Gtk.ListBox()
        self._sidebar_list.set_selection_mode(Gtk.SelectionMode.SINGLE)
        self._sidebar_list.add_css_class("navigation-sidebar")
        self._sidebar_list.connect("row-selected", self._on_sidebar_row_selected)

        for tag, icon, title_text, _ in PAGE_REGISTRY:
            row = self._make_sidebar_row(tag, icon, title_text)
            self._sidebar_list.append(row)
            self._sidebar_rows[tag] = row

        scrolled.set_child(self._sidebar_list)
        sidebar_box.append(scrolled)

        # ── Donation button at the bottom of the sidebar ────────────
        donate_btn = Gtk.Button()
        donate_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
        donate_box.set_halign(Gtk.Align.CENTER)

        coffee_icon = Gtk.Label(label="\u2615")
        coffee_icon.add_css_class("title-3")
        donate_box.append(coffee_icon)

        donate_label = Gtk.Label(label="Buy Me a Coffee")
        donate_label.add_css_class("caption")
        donate_box.append(donate_label)

        donate_btn.set_child(donate_box)
        donate_btn.add_css_class("flat")
        donate_btn.set_margin_start(12)
        donate_btn.set_margin_end(12)
        donate_btn.set_margin_top(8)
        donate_btn.set_margin_bottom(12)
        donate_btn.set_tooltip_text("Support this project \u2014 buymeacoffee.com/naftali")
        donate_btn.connect("clicked", self._on_donate_clicked)
        sidebar_box.append(donate_btn)

        toolbar.set_content(sidebar_box)
        return toolbar

    def _make_sidebar_row(self, tag: str, icon_name: str, label_text: str) -> Gtk.ListBoxRow:
        """Create a sidebar row with icon, label, and a progress checkmark."""
        row = Gtk.ListBoxRow()
        row.set_name(tag)

        box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=12)
        box.set_margin_top(8)
        box.set_margin_bottom(8)
        box.set_margin_start(12)
        box.set_margin_end(12)

        icon = Gtk.Image.new_from_icon_name(icon_name)
        icon.set_icon_size(Gtk.IconSize.NORMAL)
        box.append(icon)

        label = Gtk.Label(label=label_text)
        label.set_xalign(0)
        label.set_hexpand(True)
        box.append(label)

        # Progress indicator (hidden by default)
        check_icon = Gtk.Image.new_from_icon_name("emblem-ok-symbolic")
        check_icon.set_icon_size(Gtk.IconSize.NORMAL)
        check_icon.set_opacity(0.0)  # Hidden initially
        check_icon.add_css_class("success")
        box.append(check_icon)
        self._sidebar_checks[tag] = check_icon

        row.set_child(box)
        return row

    def _setup_keyboard_shortcuts(self) -> None:
        """Set up keyboard shortcuts for navigation."""
        controller = Gtk.EventControllerKey.new()
        controller.connect("key-pressed", self._on_key_pressed)
        self.add_controller(controller)

    def _on_key_pressed(self, controller, keyval, keycode, state) -> bool:
        """Handle keyboard shortcuts."""
        ctrl = state & Gdk.ModifierType.CONTROL_MASK

        if ctrl:
            # Ctrl+1 through Ctrl+0 for page navigation (0 = page 10)
            key_map = {
                Gdk.KEY_1: 0, Gdk.KEY_2: 1, Gdk.KEY_3: 2, Gdk.KEY_4: 3,
                Gdk.KEY_5: 4, Gdk.KEY_6: 5, Gdk.KEY_7: 6, Gdk.KEY_8: 7,
                Gdk.KEY_9: 8, Gdk.KEY_0: 9,
            }
            if keyval in key_map:
                idx = key_map[keyval]
                if idx < len(PAGE_REGISTRY):
                    tag = PAGE_REGISTRY[idx][0]
                    self.navigate_to(tag)
                    return True

            # Ctrl+Q to quit
            if keyval == Gdk.KEY_q:
                self.get_application().quit()
                return True

            # Ctrl+D to toggle dark mode
            if keyval == Gdk.KEY_d:
                self._dark_toggle.set_active(not self._dark_toggle.get_active())
                return True

        return False

    def _on_dark_toggled(self, btn) -> None:
        """Toggle between light and dark color schemes."""
        style_mgr = Adw.StyleManager.get_default()
        if btn.get_active():
            style_mgr.set_color_scheme(Adw.ColorScheme.FORCE_DARK)
            btn.set_icon_name("weather-clear-symbolic")
            btn.set_tooltip_text("Switch to light mode (Ctrl+D)")
        else:
            style_mgr.set_color_scheme(Adw.ColorScheme.FORCE_LIGHT)
            btn.set_icon_name("weather-clear-night-symbolic")
            btn.set_tooltip_text("Switch to dark mode (Ctrl+D)")

    @staticmethod
    def _on_donate_clicked(btn) -> None:
        """Open the Buy Me a Coffee donation page in the default browser."""
        url = "https://buymeacoffee.com/naftali"
        try:
            Gtk.UriLauncher.new(url).launch(None, None, None)
        except Exception:
            try:
                subprocess.Popen(
                    ["xdg-open", url],
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                )
            except FileNotFoundError:
                pass

    # ── Navigation ───────────────────────────────────────────────────
    def _on_sidebar_row_selected(self, listbox: Gtk.ListBox, row: Gtk.ListBoxRow) -> None:
        if row is None:
            return
        tag = row.get_name()
        self._stack.set_visible_child_name(tag)

        # Update content header
        for t, _, title, _ in PAGE_REGISTRY:
            if t == tag:
                self._content_title.set_title(title)
                break

        # On mobile, show content pane
        self._split.set_show_content(True)

    def navigate_to(self, tag: str) -> None:
        """Programmatically navigate to a page by tag."""
        for i, (t, _, _, _) in enumerate(PAGE_REGISTRY):
            if t == tag:
                self._sidebar_list.select_row(
                    self._sidebar_list.get_row_at_index(i)
                )
                break

    def navigate_next(self, current_tag: str) -> None:
        """Navigate to the page after *current_tag*."""
        tags = [t for t, _, _, _ in PAGE_REGISTRY]
        try:
            idx = tags.index(current_tag)
            if idx + 1 < len(tags):
                self.navigate_to(tags[idx + 1])
        except ValueError:
            pass

    def update_sidebar_progress(self, tag: str, completed: bool) -> None:
        """Update the sidebar checkmark for a given page."""
        check_icon = self._sidebar_checks.get(tag)
        if check_icon:
            check_icon.set_opacity(1.0 if completed else 0.0)

    def log_action(self, description: str) -> None:
        """Record a completed action for the summary page."""
        app = self.get_application()
        if description not in app.completed_actions:
            app.completed_actions.append(description)

    def get_completed_actions(self) -> list[str]:
        return self.get_application().completed_actions

    def show_toast(self, message: str) -> None:
        """Show an in-app toast notification via the window's ToastOverlay."""
        toast = Adw.Toast.new(message)
        toast.set_timeout(3)
        self._toast_overlay.add_toast(toast)

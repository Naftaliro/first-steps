# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright 2026 First Steps Contributors
"""Main application class — window, sidebar navigation, and page management."""

import gi

gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")

from gi.repository import Adw, Gio, GLib, Gtk

from first_steps import __app_id__, __version__
from first_steps.pages.welcome import WelcomePage
from first_steps.pages.codecs import CodecsPage
from first_steps.pages.flatpak import FlatpakPage
from first_steps.pages.drivers import DriversPage
from first_steps.pages.bottles import BottlesPage
from first_steps.pages.timeshift import TimeshiftPage
from first_steps.pages.power import PowerPage
from first_steps.pages.firewall import FirewallPage
from first_steps.pages.extras import ExtrasPage
from first_steps.pages.summary import SummaryPage


# ── Page registry ────────────────────────────────────────────────────
PAGE_REGISTRY = [
    ("welcome",   "go-home-symbolic",            "Welcome",       WelcomePage),
    ("codecs",    "media-playback-start-symbolic","Codecs & Media",CodecsPage),
    ("flatpak",   "system-software-install-symbolic","Flatpak & Apps",FlatpakPage),
    ("drivers",   "preferences-system-symbolic",  "Drivers",       DriversPage),
    ("bottles",   "preferences-desktop-apps-symbolic","Windows Apps",BottlesPage),
    ("timeshift", "drive-harddisk-symbolic",      "Backup",        TimeshiftPage),
    ("power",     "battery-symbolic",             "Power",         PowerPage),
    ("firewall",  "security-high-symbolic",       "Firewall",      FirewallPage),
    ("extras",    "applications-utilities-symbolic","Extras",       ExtrasPage),
    ("summary",   "emblem-ok-symbolic",           "Summary",       SummaryPage),
]


class FirstStepsApp(Adw.Application):
    """Top-level application object."""

    def __init__(self) -> None:
        super().__init__(
            application_id=__app_id__,
            flags=Gio.ApplicationFlags.FLAGS_NONE,
        )
        self.completed_actions: list[str] = []

    # ── activation ───────────────────────────────────────────────────
    def do_activate(self) -> None:  # noqa: D401
        win = self.props.active_window
        if not win:
            win = FirstStepsWindow(application=self)
        win.present()


class FirstStepsWindow(Adw.ApplicationWindow):
    """Main window with sidebar navigation and stacked content pages."""

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        self.set_title("First Steps")
        self.set_default_size(960, 680)
        self.set_size_request(760, 520)

        self._pages: dict[str, object] = {}
        self._build_ui()

    # ── UI construction ──────────────────────────────────────────────
    def _build_ui(self) -> None:
        # ── Navigation view (split pane) ─────────────────────────────
        self._split = Adw.NavigationSplitView()
        self._split.set_min_sidebar_width(220)
        self._split.set_max_sidebar_width(280)

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
        self._content_title = Adw.WindowTitle.new("Welcome", "Let's get your system ready")
        content_header.set_title_widget(self._content_title)
        content_toolbar.add_top_bar(content_header)
        content_toolbar.set_content(self._stack)

        content_page = Adw.NavigationPage.new(content_toolbar, "Content")
        self._split.set_content(content_page)

        self.set_content(self._split)

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

        scrolled.set_child(self._sidebar_list)
        toolbar.set_content(scrolled)
        return toolbar

    @staticmethod
    def _make_sidebar_row(tag: str, icon_name: str, label_text: str) -> Gtk.ListBoxRow:
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

        row.set_child(box)
        return row

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

    def log_action(self, description: str) -> None:
        """Record a completed action for the summary page."""
        app = self.get_application()
        if description not in app.completed_actions:
            app.completed_actions.append(description)

    def get_completed_actions(self) -> list[str]:
        return self.get_application().completed_actions

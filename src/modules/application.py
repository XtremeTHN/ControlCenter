import gi
gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")

from modules.tools.custom_widgets import VBox, HBox, create_header
from modules.tools.utilities import set_margins

from modules.widgets.appearance import AppearancePage
from modules.widgets.displays import Displays
from modules.widgets.energy import Energy

from modules.variables import app

from gi.repository import Gtk, Adw, Gio, GLib

def create_placeholder() -> VBox:
    """Creates a placeholder

    Returns:
        VBox: A VBox containing the placeholder widgets
    """
    _placeholder = VBox(spacing=0, vexpand=True, hexpand=True)
    _placeholder.set_valign(Gtk.Align.CENTER)

    placeholder_image = Gtk.Image(icon_name="preferences-system-symbolic")
    placeholder_image.set_pixel_size(90)
    placeholder_image.set_opacity(0.7)

    placeholder_title = Gtk.Label.new("<span weight=\"bold\" size=\"larger\">Welcome to Control Center!</span>")
    placeholder_title.set_use_markup(True)

    _placeholder.append(placeholder_image)
    _placeholder.append(placeholder_title)

    return _placeholder

class ControlCenterGroup(Gtk.ListBox):
    def __init__(self, is_root=False, **extra):
        super().__init__(**extra)
        if is_root is False:
            self.add_css_class('navigation-sidebar')

    def append_button(self, icon, label, target):
        btt = Gtk.ListBoxRow.new()
        
        btt_content = HBox(name=f"{target}-button")

        btt_content_image = Gtk.Image.new_from_icon_name(icon)
        btt_content_label = Gtk.Label.new(label)

        btt_content.appends(btt_content_image, btt_content_label)
        
        btt.set_child(btt_content)

        self.append(btt)


class ControlCenterSideBar:
    def __init__(self):
        self.children: dict[str, Adw.NavigationPage] = {}
        
        self.split_view = Adw.NavigationSplitView(min_sidebar_width=200, hexpand=True, vexpand=True)
        
        self.sidebar_page = Adw.NavigationPage(title="Control Center", tag="sidebar")

        # A widget holding the header and the content
        self.sidebar, _ = create_header()

        self.sidebar_content = ControlCenterGroup(is_root=True)
        self.sidebar_content.connect('row-activated', self.on_row_activate)

        self.sidebar.set_content(self.sidebar_content)

        self.sidebar_page.set_child(self.sidebar)

        self.placeholder_page = Adw.NavigationPage(title="Control Center", tag="content")

        self.placeholder, _= create_header()
        
        self.placeholder_content = create_placeholder()

        self.placeholder_page.set_child(self.placeholder_content)

        self.split_view.set_sidebar(self.sidebar_page)
        self.split_view.set_content(self.placeholder_page)
        
    def add_named(self, widget, tag, title):
        if isinstance(widget, Gtk.Widget):
            self.children[tag] = Adw.NavigationPage(child=widget, title=title, tag=tag)
        elif hasattr(widget, "widget") is True:
            self.children[tag] = Adw.NavigationPage(child=widget.widget, title=title, tag=tag)
        else:
            print("WARNING: Expected Adw.NavigationPage on ControlCenterSideBar, no", type(widget))
    
    def append_button(self, icon, label, target):
        btt = Gtk.ListBoxRow.new()
        
        btt_content = HBox(name=f"{target}-button")

        btt_content_image = Gtk.Image.new_from_icon_name(icon)
        btt_content_label = Gtk.Label.new(label)

        btt_content.appends(btt_content_image, btt_content_label)
        
        btt.set_child(btt_content)

        self.sidebar_content.append(btt)
    
    def create_group(self):
        group_content = ControlCenterGroup()
        group_content.connect('row-activated', self.on_row_activate)

        self.sidebar_content.append(Gtk.Separator.new(orientation=Gtk.Orientation.HORIZONTAL))
        self.sidebar_content.append(group_content)
        self.sidebar_content.append(Gtk.Separator.new(orientation=Gtk.Orientation.HORIZONTAL))

        return group_content
    
    def append_both(self, widget, name, icon, label):
        self.add_named(widget, name, label)
        self.append_button(icon, label, name)

    def on_row_activate(self, listbox, row: Gtk.ListBoxRow, *args):
        target_name = row.get_first_child().get_name().split('-')[0]
        
        if self.split_view.props.content.get_name() != target_name:
            self.split_view.set_content(self.children[target_name])
            self.split_view.activate_action("navigation.push", GLib.Variant.new_string(target_name))

class ControlCenterWindow(Adw.ApplicationWindow):
    def __init__(self, app):
        super().__init__(application=app)
        self.set_default_size(1024, 900)
        self.set_title("Control Center")
        
        self.main = HBox()

        self.content = ControlCenterSideBar()

        self.content.append_both(AppearancePage(self), "appearance", "preferences-system-symbolic", "Appearance")
        
        self.content.append_both(Energy(), "energy", "battery-full-symbolic", "Energy")

        hypr_group = self.content.create_group()
        hypr_group.append_button("applications-display-symbolic", "Displays", "displays")

        self.main.append(self.content.split_view)

        self.set_content(self.main)

        self.present()
    
    def color_callback(self, widget, color_scheme_name):
        if widget.get_active():
            print("Yes", color_scheme_name)
    
    def toggle_placeholder(self, toggled=None):
        self._placeholder.set_visible(not self.get_visible() if toggled is None else toggled)

class ControlCenter(Adw.Application):
    def __init__(self):
        super().__init__(
            application_id="com.github.XtremeTHN.ControlCenter1",
            flags=Gio.ApplicationFlags.FLAGS_NONE
        )
    
    def do_activate(self) -> None:
        if not self.props.active_window:
            ControlCenterWindow(self)
        
        self.create_action('quit', self.exit_app, ['<primary>q'])
    
    def exit_app(self, action, param):
        self.quit()
    
    def create_action(self,name, callback, shortcuts=None):
        action = Gio.SimpleAction.new(name, None)
        action.connect('activate', callback)
        self.add_action(action)

        if shortcuts:
            self.set_accels_for_action(f'app.{name}', shortcuts)

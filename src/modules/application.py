import gi
gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")
from modules.tools import VBox, HBox, set_margins, create_header
from modules.widgets.appearance import AppearancePage
from modules.widgets.displays import Displays
from gi.repository import Gtk, Adw, Gio, Gdk

class ControlCenterSideBar:
    def __init__(self):
        self.split_view = Adw.NavigationSplitView(show_content=True, min_sidebar_width=200, hexpand=True, vexpand=True)
        
        self.sidebar_page = Adw.NavigationPage(title="Control Center", tag="sidebar")

        # A widget holding the header and the content
        self.sidebar, self.sidebar_header = create_header()

        self.sidebar_content = Gtk.ListBox.new()
        self.sidebar_content.connect('row-activated', self.on_row_activate)

        self.sidebar_content.set_selection_mode(Gtk.SelectionMode.NONE)
        self.sidebar_content.add_css_class('navigation-sidebar')

        self.sidebar.set_content(self.sidebar_content)

        self.sidebar_page.set_child(self.sidebar)

        self.content_page = Adw.NavigationPage(title="Control Center", tag="content")

        self.content, self.content_header = create_header()

        self.stack = Gtk.Stack(transition_duration=500, transition_type=Gtk.StackTransitionType.SLIDE_LEFT_RIGHT)
        set_margins(self.stack, [0,10,0,10])

        self.content.set_content(self.stack)

        self.content_page.set_child(self.content)

        self.split_view.set_sidebar(self.sidebar_page)
        self.split_view.set_content(self.content_page)
    
    def append_button_to_sidebar(self, icon, label, target):
        btt_content = HBox(name=f"{target}-button")

        btt_content_image = Gtk.Image.new_from_icon_name(icon)
        btt_content_label = Gtk.Label.new(label)

        btt_content.appends(btt_content_image, btt_content_label)

        self.sidebar_content.append(btt_content)

    def append_to_stack(self, widget: Gtk.Widget, name: str):
        self.stack.add_named(widget, name)
    
    def append_both(self, widget, name, icon, label):
        self.append_to_stack(widget, name)
        self.append_button_to_sidebar(icon, label, name)

    def on_row_activate(self, listbox, row: Gtk.ListBox, *args):
        self.stack.set_visible_child_name(row.get_first_child().get_name().split('-')[0])

class ControlCenterWindow(Adw.ApplicationWindow):
    def __init__(self, app):
        super().__init__(application=app)
        self.set_default_size(1024, 900)
        self.set_title("Control Center")
        
        self.main = HBox()

        self.content = ControlCenterSideBar()

        self.content.append_to_stack(self.create_placeholder(), "placeholder")
        self.content.append_both(AppearancePage(), "appearance", "preferences-system-symbolic", "Appearance")

        self.content.append_both(Displays(), "displays", "applications-display-symbolic", "Displays")

        self.main.append(self.content.split_view)

        self.set_content(self.main)

        self.present()
    
    def color_callback(self, widget, color_scheme_name):
        if widget.get_active():
            print("Yes", color_scheme_name)
    
    def create_placeholder(self):
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
    
    def toggle_placeholder(self, toggled=None):
        self._placeholder.set_visible(not self.get_visible() if toggled is None else toggled)

class ControlCenter(Adw.Application):
    def __init__(self):
        super().__init__(
            application_id="com.github.XtremeTHN.ControlCenter1",
            flags=Gio.ApplicationFlags.FLAGS_NONE
        )
    
    def do_activate(self) -> None:
        #        res = Gio.Resource.load('src/res/com.github.XtremeTHN.ControlCenter.gresource')
        #Gio.resources_register(res)

        Adw.StyleManager().set_color_scheme(Adw.ColorScheme.FORCE_DARK)

        self.win = self.props.active_window
        if not self.win:
            self.win = ControlCenterWindow(self)
        
        self.create_action('quit', self.exit_app, ['<primary>q'])
    
    def exit_app(self, action, param):
        self.quit()
    
    def create_action(self,name, callback, shortcuts=None):
        action = Gio.SimpleAction.new(name, None)
        action.connect('activate', callback)
        self.add_action(action)

        if shortcuts:
            self.set_accels_for_action(f'app.{name}', shortcuts)

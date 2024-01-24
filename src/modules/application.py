import gi
gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")
from modules.tools import VBox, HBox, set_margins
from modules.appearance import AppearancePage, ColorScheme
from gi.repository import Gtk, Adw, Gio, Gdk

class ControlCenterSideBar(HBox):
    def __init__(self, transition_type):
        super().__init__(spacing=0)

        self.sidebar = VBox(spacing=0)
        self.sidebar.set_size_request(200, 1)
        self.sidebar.add_css_class('sidebar')

        self.sidebar_content = VBox(spacing=2)
        set_margins(self.sidebar_content, [10])

        self.sidebar_header = Adw.HeaderBar.new()
        self.sidebar_header.set_title_widget(Gtk.Label(label="Configuration"))
        self.sidebar_header.set_show_end_title_buttons(False)
        self.sidebar_header.pack_end(Gtk.Button.new_from_icon_name("open-menu-symbolic"))
        
        self.main_box = VBox(spacing=0)
        self.content_box = VBox(spacing=2, hexpand=True)
        set_margins(self.content_box, [10])

        self.main_box_header_title = Gtk.Label(label="Control Center")
        self.main_box_header = Adw.HeaderBar(title_widget=self.main_box_header_title, hexpand=True)

        self.stack = Gtk.Stack(transition_duration=500, transition_type=transition_type)
        self.main_box_header_title.bind_property("label", self.stack, "visible-child-name")

        self.sidebar.appends(self.sidebar_header, self.sidebar_content)
        self.content_box.append(self.stack)
        self.main_box.appends(self.main_box_header, self.content_box)

        self.appends(self.sidebar, self.main_box)
    
    def append_to_stack(self, widget: Gtk.Widget, name: str):
        self.stack.add_named(widget, name)

    def append_button_to_sidebar(self, icon, label, target):
        btt = Gtk.Button.new()

        btt.add_css_class('sidebar-button')

        btt_content = HBox()
        btt_content_image = Gtk.Image.new_from_icon_name(icon)
        btt_content_label = Gtk.Label.new(label)

        btt_content.appends(btt_content_image, btt_content_label)

        btt.set_child(btt_content)

        btt.connect('clicked', lambda _: self.stack.set_visible_child_name(target))

        self.sidebar_content.append(btt)

    def append_both(self, widget, name, icon, label):
        self.append_to_stack(widget, name)
        self.append_button_to_sidebar(icon, label, name)

class ControlCenterWindow(Adw.ApplicationWindow):
    def __init__(self, app):
        super().__init__(application=app)
        self.set_default_size(1024, 800)
        self.set_title("Control Center")
        
        self.main = HBox()

        self.sidebar = ControlCenterSideBar(Gtk.StackTransitionType.SLIDE_LEFT_RIGHT)

        self.sidebar.append_to_stack(self.create_placeholder(), "placeholder")
        self.sidebar.append_both(AppearancePage(), "appearance", "preferences-system-symbolic", "Appearance")

        self.main.append(self.sidebar)

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
        Adw.StyleManager(color_scheme=Adw.ColorScheme.PREFER_DARK, display=Gdk.Display.get_default())

        provider = Gtk.CssProvider.new()
        provider.load_from_path('src/styles/style.css')

        Gtk.StyleContext.add_provider_for_display(
            Gdk.Display.get_default(),
            provider,
            Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
        )

        res = Gio.Resource.load('src/res/com.github.XtremeTHN.ControlCenter.gresource')
        Gio.resources_register(res)

        self.win = self.props.active_window
        if not self.win:
            self.win = ControlCenterWindow(self)
            # self.win = TestWindow(self)
        
        self.create_action('quit', self.exit_app, ['<primary>q'])
    
    def exit_app(self, action, param):
        self.quit()
    
    def create_action(self,name, callback, shortcuts=None):
        action = Gio.SimpleAction.new(name, None)
        action.connect('activate', callback)
        self.add_action(action)

        if shortcuts:
            self.set_accels_for_action(f'app.{name}', shortcuts)
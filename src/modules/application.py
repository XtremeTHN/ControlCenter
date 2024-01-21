import gi
gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")
from modules.tools import VBox, HBox
from gi.repository import Gtk, Adw, Gio, Gdk

class ControlCenterWindow(Adw.ApplicationWindow):
    def __init__(self, app):
        super().__init__(application=app)
        self.set_default_size(1024, 800)
        self.set_title("Control Center")
        
        self.main = HBox()

        self.sidebar_box = VBox()
        # self.sidebar_header = Adw.HeaderBar.new()
        self.sidebar = Gtk.StackSidebar.new()
        self.sidebar.set_vexpand(True)

        # self.sidebar_box.append(self.sidebar_header)
        self.sidebar_box.append(self.sidebar)
        
        self.stack = Gtk.Stack.new()
        self.stack.add_named(self.create_placeholder(), 'placeholder')

        self.main.append(self.sidebar_box)
        self.main.append(self.stack)

        self.set_content(self.main)

        self.present()
    
    def create_placeholder(self):
        _placeholder = VBox(spacing=0, vexpand=True, hexpand=True)
        _placeholder.set_valign(Gtk.Align.CENTER)

        placeholder_image = Gtk.Image(icon_name="preferences-system-symbolic")
        placeholder_image.set_pixel_size(90)
        placeholder_image.set_opacity(0.7)

        placeholder_title = Gtk.Label.new("<span weight=\"bold\" size=\"larger\">Welcome to Control Center!</span>")
        placeholder_title.set_use_markup(True)

        placeholder_subtitle = Gtk.Label.new("<span size=\"smaller\" weight=\"light\">This control center is made specially for Hyprland and you need to installl my dotfiles to use it!</span>")

        placeholder_subtitle.set_use_markup(True)
        placeholder_subtitle.set_wrap(True)
        placeholder_subtitle.set_wrap_mode(Gtk.WrapMode.WORD)

        _placeholder.append(placeholder_image)
        _placeholder.append(placeholder_title)
        _placeholder.append(placeholder_subtitle)

        return _placeholder
    
    def toggle_placeholder(self, toggled=None):
        self._placeholder.set_visible(not self.get_visible() if toggled is None else toggled)

class TestWindow(Adw.ApplicationWindow):
    def __init__(self, app):
        super().__init__(application=app)

        self.set_default_size(800, 600)
        self.set_size_request(800, 600)

        self.main_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)
        self.header = Adw.HeaderBar.new()
        self.header.set_title_widget(Gtk.Label(label=""))

        self.main_box.append(self.header)

        self.set_content(self.main_box)

        self.present()

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
import gi
gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")

from gi.repository import Gtk, Adw, Gio, Gdk

class ControlCenterWindow(Adw.ApplicationWindow):
    def __init__(self, app):
        super().__init__(application=app)
        self.set_default_size(1024, 800)
        self.set_title("Control Center")
        
        self.sidebar_content = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        self.sidebar_headerbar = Adw.HeaderBar.new()
        self.sidebar_content.append(self.sidebar_headerbar)

        self.sidebar = Adw.NavigationPage.new(self.sidebar_content, title="Control Center")
        
        self.placeholder = self.create_placeholder()

        self.preferencesActive = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6, valign=Gtk.Align.CENTER)
        self.preferencesActive.append(self.placeholder)

        self.preferencePage = Adw.NavigationPage.new(self.preferencesActive, "Preferences")

        self.content = Adw.NavigationSplitView(sidebar=self.sidebar, content=self.preferencePage)

        self.set_content(self.content)

        self.present()
    
    def create_placeholder(self):
        self._placeholder = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)

        self.placeholder_image = Gtk.Image(icon_name="preferences-system-symbolic")
        self.placeholder_image.set_pixel_size(90)
        self.placeholder_image.set_opacity(0.7)

        self.placeholder_title = Gtk.Label.new("<span weight=\"bold\" size=\"larger\">Welcome to Control Center!</span>")
        self.placeholder_title.set_use_markup(True)

        self.placeholder_subtitle = Gtk.Label.new("<span size=\"smaller\" weight=\"light\">This control center is made specially for Hyprland and you need to installl my dotfiles to use it!</span>")

        self.placeholder_subtitle.set_use_markup(True)
        self.placeholder_subtitle.set_wrap(True)
        self.placeholder_subtitle.set_wrap_mode(Gtk.WrapMode.WORD)

        self._placeholder.append(self.placeholder_image)
        self._placeholder.append(self.placeholder_title)
        self._placeholder.append(self.placeholder_subtitle)

        return self._placeholder
    
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
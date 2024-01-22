import gi
gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")
from modules.tools import VBox, HBox
from gi.repository import Gtk, Adw, Gio, Gdk

class ControlCenterSideBar(HBox):
    def __init__(self, transition_type):
        self.sidebar = VBox(spacing=2)
        self.sidebar.set_size_request(200, -1)
        self.stack = Gtk.Stack(transition_duration=500, transition_type=transition_type)
        super().__init__()

        self.sidebar.add_css_class('sidebar')

        self.header = Adw.HeaderBar.new()
        self.header.set_title_widget(Gtk.Label(label="Control Center"))
        self.header.set_show_end_title_buttons(False)
        self.header.pack_end(Gtk.Button.new_from_icon_name("open-menu-symbolic"))

        self.sidebar.append(self.header)
        self.appends(self.sidebar, self.stack)
    
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

        self.sidebar.append(btt)

class ControlCenterWindow(Adw.ApplicationWindow):
    def __init__(self, app):
        super().__init__(application=app)
        self.set_default_size(1024, 800)
        self.set_title("Control Center")
        
        self.main = HBox()

        self.sidebar = ControlCenterSideBar(Gtk.StackTransitionType.SLIDE_LEFT_RIGHT)

        self.sidebar.append_to_stack(self.create_placeholder(), "placeholder")
        self.sidebar.append_to_stack(Gtk.Label.new("Search"), "search")
        self.sidebar.append_button_to_sidebar("system-search-symbolic", "Search", "search")

        self.main.append(self.sidebar)

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

        # placeholder_subtitle = Gtk.Label.new("<span size=\"smaller\" weight=\"light\">This control center is made specially for Hyprland and you need to installl my dotfiles to use it!</span>")

        # placeholder_subtitle.set_use_markup(True)
        # placeholder_subtitle.set_wrap(True)
        # placeholder_subtitle.set_wrap_mode(Gtk.WrapMode.WORD)

        _placeholder.append(placeholder_image)
        _placeholder.append(placeholder_title)
        # _placeholder.append(placeholder_subtitle)

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
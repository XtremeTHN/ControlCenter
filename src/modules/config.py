from gi.repository import Gio
import os
import toml

class BaseConfiguration(Gio.Settings):
    def __init__(self, schema):
        super().__init__(schema=schema)
    
    def connect_changed_config(self, callback, prop):
        self.connect(f"changed::{prop}", callback)
    
    def bind_config(self, key, widget, prop):
        self.bind(key, widget, prop, Gio.SettingsBindFlags.DEFAULT)

class AppearanceConfig(BaseConfiguration):
    def __init__(self):
        super().__init__("com.github.XtremeTHN.ControlCenter.Appearance")

    def bindCursorTheme(self, widget, prop):
        self.bind_config("cursor-theme", widget, prop)

    def bindGtkTheme(self, widget, prop):
        self.bind_config("gtk-theme", widget, prop)

    def bindIconTheme(self, widget,prop):
        self.bind_config("icon-theme", widget, prop)
    
    def bindWallpaper(self, widget, prop):
        self.bind_config("wallpaper", widget, prop)

class LoginManagerConfig(BaseConfiguration):
    class LoginManagerAutoLoginConfig(BaseConfiguration):
        def __init__(self):
            super().__init__("com.github.XtremeTHN.ControlCenter.LoginManager.AutoLogin")
        
        def bindEnabled(self, widget, prop):
            self.bind_config("enabled", widget, prop)

        def bindUser(self, widget, prop):
            self.bind_config("user", widget, prop)
        
        def bindPassword(self, widget, prop):
            self.bind_config("password", widget, prop)
        
        def bindSession(self, widget, prop):
            self.bind_config("session", widget, prop)

    def __init__(self):
        super().__init__("com.github.XtremeTHN.ControlCenter.LoginManager")

    def bindTheme(self, widget, prop):
        self.config.bind("theme", widget, prop, Gio.SettingsBindFlags.DEFAULT)

class NotificationsConfig(BaseConfiguration):
    class NotificationsAppearanceConfig(BaseConfiguration):
        def __init__(self):
            super().__init__("com.github.XtremeTHN.ControlCenter.Notifications.Appearance")
        
        def bindBlur(self, widget, prop):
            self.bind_config("blur", widget, prop)
        
        def bindOpacity(self, widget, prop):
            self.bind_config("opacity", widget, prop)
        
    def __init__(self):
        super().__init__("com.github.XtremeTHN.ControlCenter.Notifications")
    
    def bindDnd(self, widget, prop):
        self.bind_config("dnd", widget, prop)
    
    def bindDuration(self, widget, prop):
        self.bind_config("duration", widget, prop)

class PlymouthConfig(BaseConfiguration):
    def __init__(self):
        super().__init__("com.github.XtremeTHN.ControlCenter.Plymouth")
    
    def bindEnabled(self, widget, prop):
        self.bind_config("enabled", widget, prop)
    
    def bindTheme(self, widget, prop):
        self.bind_config("theme", widget, prop)
    
class UserConfig(BaseConfiguration):
    def __init__(self):
        super().__init__("com.github.XtremeTHN.ControlCenter.User")
    
    def bindName(self, widget, prop):
        self.bind_config("user-name", widget, prop)
    
    def bindPhoto(self, widget, prop):
        self.bind_config("user-photo", widget, prop)

class GtkConfig(BaseConfiguration):
    def __init__(self):
        super().__init__('org.gnome.desktop.interface')
        gtk_config_path = os.path.expanduser("~/.config/gtk-4.0")
        gtk_config_file_path = os.path.join(gtk_config_path, "settings.ini")

        if not os.path.exists(gtk_config_path):
            os.system(f'mkdir -p {gtk_config_path}')

        if not os.path.exists(gtk_config_file_path):
            os.system(f'touch {gtk_config_file_path}')
        
        self.config_file = toml.load(open(gtk_config_file_path))

    def set_theme(self, theme):
        self.set_string('gtk-theme', theme)

    def set_dark_scheme(self, enabled):
        self.config_file['gtk-application-prefer-dark-theme'] = enabled

    def set_light_scheme(self, enabled):
        self.config_file['gtk-application-prefer-light-theme'] = enabled

    def bindTheme(self, widget, prop):
        self.bind_config("theme", widget, prop)
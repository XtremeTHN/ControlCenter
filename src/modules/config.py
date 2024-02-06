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
        self.font_value = self.get_string('font-name').split(' ')

    def set_theme(self, theme):
        self.set_string('gtk-theme', theme)
    
    def _set_font(self):
        self.set_string('font-name', " ".join(self.font_value))

    def set_font_name(self, name: str):
        self.font_value[0] = name.strip()
        self._set_font()
    
    def set_font_size(self, size: int):
        self.font_value[1] = str(size)
        self._set_font()

    def bindTheme(self, widget, prop):
        self.bind_config("theme", widget, prop)
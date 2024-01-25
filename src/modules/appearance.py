from modules.config import AppearanceConfig
from modules.tools import set_margins, VBox, HBox

from gi.repository import Gtk, GdkPixbuf, Adw, Gio

def ColorScheme(color_scheme_name: str, subtitle: str, img_name: str, callback):
    border_box = Gtk.ToggleButton.new()
    # border_box.add_css_class('colorscheme-button-border')

    box = VBox(spacing=0)
    
    img = Gtk.Image.new_from_resource(f'/com/github/XtremeTHN/ControlCenter/src/res/uncompiled/{img_name}.png')
    img.set_pixel_size(168)
    img.add_css_class('colorscheme-img')
    box_foot_text = Gtk.Label.new(subtitle)
    
    box.appends(img, box_foot_text)
    border_box.set_child(box)

    border_box.connect('toggled', callback, color_scheme_name)

    return border_box


class AppearancePage(VBox):
    def __init__(self):
        # AppearanceConfig.__init__(self)
        super().__init__(spacing=10)
        
        color_schemes_group = Adw.PreferencesGroup()
        color_schemes_group.set_title("Style")
        color_schemes_group.set_description("Choose a color scheme")

        cs_buttons = HBox(homogeneous=True)
        
        light = ColorScheme("light", "Light", "light-color-scheme", self.color_callback)
        dark = ColorScheme("dark", "Dark", "dark-color-scheme", self.color_callback)

        cs_buttons.appends(light, dark)

        color_schemes_group.add(cs_buttons)
        self.append(color_schemes_group)

    def color_callback(self, widget, color_scheme_name):
        if widget.get_active():
            print("Yes", color_scheme_name)

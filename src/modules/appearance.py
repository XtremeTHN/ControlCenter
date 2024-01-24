from modules.config import AppearanceConfig
from modules.tools import set_margins, VBox, HBox

from gi.repository import Gtk, GdkPixbuf, Adw, Gio

def ColorScheme(color_scheme_name: str, subtitle: str, img_name: str, callback):
    border_box = Gtk.ToggleButton.new()
    # border_box.add_css_class('colorscheme-button-border')

    box = VBox(spacing=0)
    
    box_img = Gtk.Image.new_from_resource(f'/com/github/XtremeTHN/ControlCenter/src/res/uncompiled/{img_name}.png')
    box_img.set_pixel_size(214)
    box_img.add_css_class('colorscheme-img')
    box_foot_text = Gtk.Label.new(subtitle)
    
    box.appends(box_img, box_foot_text)
    border_box.set_child(box)

    border_box.connect('toggled', callback, color_scheme_name)

    return border_box


class AppearancePage(VBox):
    def __init__(self):
        # AppearanceConfig.__init__(self)
        super().__init__(spacing=10)
        
        self.color_scheme_box = VBox(spacing=0)
        self.color_scheme_box_title = Gtk.Label(label='<span weight="bold">Style</span>', use_markup=True, halign=Gtk.Align.START)
        self.color_scheme_box_color_schemes = HBox(spacing=20)
        set_margins(self.color_scheme_box_color_schemes, [10])

        self.color_scheme_box_color_schemes.appends(ColorScheme("Dark", "dark", "dark-color-scheme", self.color_callback))
        self.color_scheme_box.appends(self.color_scheme_box_title, self.color_scheme_box_color_schemes)
        self.append(self.color_scheme_box)

    def color_callback(self, widget, color_scheme_name):
        if widget.get_active():
            print("Yes", color_scheme_name)

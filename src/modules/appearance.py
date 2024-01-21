from modules.config import AppearanceConfig
from modules.tools import set_margins, VBox, HBox

from gi.repository import Gtk, Adw

def ColorScheme(color_scheme_name: str, callback: function):
    box = VBox()
    

class AppearancePage(AppearanceConfig):
    def __init__(self):
        super().__init__()

        self.content = Gtk.Box.new(Gtk.Orientaton.VERTICAL, 10)
        
        self.color_scheme_box = VBox(spacing=0)
        self.color_scheme_box_title = Gtk.Label(label="<span weight=bold>Style</span>", use_markup=True)
        self.color_scheme_box_color_schemes = HBox(spacing=20)
        set_margins(self.color_scheme_box_color_schemes, [10])


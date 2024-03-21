from modules.upower import UPowerManager
from modules.tools.custom_widgets import ConfigPage, VBox

from gi.repository import Adw, Gtk

class Energy(ConfigPage):
    def __init__(self):
        super().__init__("Energy")
        self.stack = Gtk.Stack.new()
        
        self.no_battery_available = Adw.StatusPage(icon_name="battery-missing-symbolic", vexpand=True, valign=Gtk.Align.CENTER, title="Missing battery", description="Without a battery, you cannot see this page")
        self.stack.add_named(self.no_battery_available, "no-batt-avail")
        
        self.content = VBox()
        self.stack.add_named(self.content, "content")
        
        self.scroll_box.append(self.stack)
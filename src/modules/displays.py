from modules.tools import include_file, create_empty_file
from modules.hyprland.ctl import HyprCtl, Monitor

import logging
import 
import os

class Displays(HyprCtl):
    """
        Parse the monitor config file.
        Monitor config goes in this order:
        MONITOR_NAME,RESOLUTION@MON_HERTZ,POSITION,FRACTIONAL_SCALE
    """
    def __init__(self):
        super().__init__()
        self.logger = logging.getLogger("Displays")
        self.file_path = os.path.expanduser("~/.config/hypr/")
        if not os.path.exists(self.file_path):
            self.logger.error("Hyprland config doesn't exists!")
            return
        
        self.hypr_monitor_file_path = os.path.join(self.file_path, "monitors.conf")
        if not os.path.exists(self.hypr_monitor_file_path):
            self.logger.error("Hyprland monitors config file doesn't exists! Creating it...")
            create_empty_file(self.hypr_monitor_file_path)

    def get_monitors(self):
        return self.getMonitors()

    def serialize(self, monitors: list[Monitor]):
        monitors_string_list = []
        for x in monitors:
            string = "monitor="
            string += f"{x.name},"
            string += f"{x.width}x{x.height}@{int(x.refreshRate)},"
            string += f"{x.x}x{x.y},"
            string += str(x.scale)
            string += "\n"

            monitors_string_list.append(string)
        
        with open(self.hypr_monitor_file_path, 'w') as file:
            file.writelines(monitors_string_list)
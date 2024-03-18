from modules.tools import create_empty_file
from modules.hyprland.ctl import HyprCtl, Monitor
from datetime import datetime

import logging
import shutil
import os

class Monitors:
    """
        Gets the list of monitors from Hyprland Ctl.
        Customize the monitor config with the monitors list property.
        See Monitor class for more details.
    """
    def __init__(self):
        self.__ctl = HyprCtl()
        
        self.__logger = logging.getLogger("Displays")
        self.__file_path = os.path.expanduser("~/.config/hypr/")
        if not os.path.exists(self.__file_path):
            self.__logger.error("Hyprland config doesn't exists!")
            return
        
        self.hypr_monitor_file_path = os.path.join(self.__file_path, "monitors.conf")
        if not os.path.exists(self.hypr_monitor_file_path):
            self.__logger.error("Hyprland monitors config file doesn't exists! Creating it...")
            create_empty_file(self.hypr_monitor_file_path)

        self.monitors: list[Monitor] = self.__ctl.getMonitors()
    
    def update_monitors_list(self):
        self.monitors: list[Monitor] = self.__ctl.getMonitors()

    def serialize(self):
        """
        Serialize the monitors list into a string

        Monitor config goes in this order:
        MONITOR_NAME,RESOLUTION@MON_HERTZ,POSITION,FRACTIONAL_SCALE

        Other configurations will be ignored.
        """
        monitors_string_list = [f"# Edited by Control Center ({datetime.now().strftime('%Y-%m-%d %H:%M')})\n"]
        for x in self.monitors:
            string = "monitor="
            string += f"{x.name},"
            string += f"{x.width}x{x.height}@{int(x.refreshRate)},"
            string += f"{x.x}x{x.y},"
            string += str(x.scale)
            string += "\n"

            monitors_string_list.append(string)

        return monitors_string_list

    def save(self):
        """
        Serialize the monitors list into a string and saves it to ~/.config/hypr/monitors.conf 

        Monitor config goes in this order:
        MONITOR_NAME,RESOLUTION@MON_HERTZ,POSITION,FRACTIONAL_SCALE

        Other configurations will be ignored.
        """
        monitors_string_list = self.serialize()
        
        shutil.move(self.hypr_monitor_file_path, self.hypr_monitor_file_path + ".bak")
        with open(self.hypr_monitor_file_path, 'w') as file:
            file.writelines(monitors_string_list)
    
    def get_monitor(self, id) -> Monitor:
        return list(filter(lambda x: x.id == id, self.monitors))[0]
from modules.tools import include_file, create_empty_file
from modules.hyprland.ctl import HyprCtl

import logging
import os

class Displays:
    def __init__(self):
        self.logger = logging.getLogger("Displays")
        self.file_path = os.path.expanduser("~/.config/hypr/")
        if not os.path.exists(self.file_path):
            self.logger.error("Hyprland config doesn't exists!")
            return
        
        self.hypr_monitor_file_path = os.path.join(self.file_path, "monitors.conf")
        if not os.path.exists(self.hypr_monitor_file_path):
            self.logger.error("Hyprland monitors config file doesn't exists! Creating it...")
            create_empty_file(self.hypr_monitor_file_path)

        self.hypr_monitor_file = include_file(self.hypr_monitor_file_path)
        self.logger.info("Parsing monitor files...")
        self._parse_conf_file(self.hypr_monitor_file)

    def _parse_conf_file(self, content: str):
        for lineno, line in enumerate(content.splitlines()):
            if line.startswith("#"):
                continue
            try:
                mon_conf = line.split("=")
                if mon_conf[0] != "monitor":
                    continue

            except Exception as e:
                self.logger.warning(f"Error while parsing line {lineno} on monitors.conf")
                self.logger.debug(f"Exception: {e}")

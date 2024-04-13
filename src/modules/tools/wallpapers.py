from glob import glob
from gi.repository import Adw, Gtk
from modules.hyprland.ctl import HyprCtl
from modules.tools.custom_widgets import VBox

from gi.repository import GObject

import os
import logging
import subprocess

class WallpaperBackendTemplate(GObject.GObject):
    __gsignals__ = {
        'changed': (GObject.SignalFlags.RUN_FIRST, None, ())
    }
    def __init__(self, cmd):
        super().__init__()
        self.logger = logging.getLogger("WallpaperBackendTemplate")
        if subprocess.check_output(args=["which",cmd]).startswith(b"which: no"):
            self.logger.warning(f"Detected backend '{cmd}' but no executable file has been founded")
            self.executable_exists = False
            return
        
        self.logger.info(f"Detected backend '{cmd}'")

        self.executable_exists = True
        self.cmd = cmd

    def exec(self, *args):
        """Execs the cmd with args
        """
        return subprocess.check_output(args=[self.cmd, *args])
    
    def set_wallpaper(self, wallpaper_path):
        ...
    def get_wallpaper(self):
        ...
    def get_version(self):
        ...

class Swww(WallpaperBackendTemplate):
    def __init__(self):
        super().__init__("swww")
    
    def get_wallpaper(self):
        return self.exec("query").decode().split(":")[-1].strip()

    def set_wallpaper(self, wallpaper_path):
        self.emit('changed')
        return self.exec("img", wallpaper_path)
    
    def get_version(self):
        return self.exec("-V").decode("utf-8").strip()

class Wallpapers:
    def __init__(self):
        self.logger = logging.getLogger("Wallpapers")
        
        self.__ctl = HyprCtl()
        
    def get_backend(self):
        self.logger.info("Detecting wallpaper backend")
        
        layers = self.__ctl.getLayers()
        for display in layers:
            for wallpaper_helper in layers[display]["levels"]["0"]:
                if wallpaper_helper["namespace"] == "swww":
                    return Swww()
    
    def get_wallpapers(self) -> list[str]:
        extensions = ["*.jpg", "*.png", "*.jpeg"]
        
        files = []
        for ext in extensions:
            for file in glob(os.getenv("HOME") + "/Pictures/" + ext):
                if os.path.isfile(file):
                    files.append(file)
        return files
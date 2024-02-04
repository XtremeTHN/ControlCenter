from gi.repository import Gtk, Gio, GObject
from modules.config import GtkConfig
from glob import glob

import os
import logging

def set_margins(widget: Gtk.Widget, margins: list[int]):
    length = len(margins)
    
    top = margins[0]
    right = margins[1] if length > 1 else top
    bottom = margins[2] if length > 2 else right
    left = margins[3] if length > 3 else bottom

    widget.set_margin_top(top)
    widget.set_margin_end(right)
    widget.set_margin_bottom(bottom)
    widget.set_margin_start(left)

def include_file(file: str) -> str:
    gfile = Gio.File.new_for_path(file)

    return gfile.load_contents(None)[1].decode('utf-8')

def include_bytes(file: str) -> bytes:
    gfile = Gio.File.new_for_path(file)
    return gfile.load_contents(None)[1]



class HBox(Gtk.Box):
    def __init__(self, spacing=10, **extra):
        super().__init__(orientation=Gtk.Orientation.HORIZONTAL, spacing=spacing, **extra)
    
    def appends(self, *widgets):
        for widget in widgets:
            self.append(widget)

class VBox(Gtk.Box):
    def __init__(self, spacing=10, **extra):
        super().__init__(orientation=Gtk.Orientation.VERTICAL, spacing=spacing, **extra)
    
    def appends(self, *widgets):
        for widget in widgets:
            self.append(widget)

class GtkThemes(GtkConfig, GObject.GObject):
    def __init__(self):
        GtkConfig.__init__(self)
        GObject.GObject.__init__(self)

        self.logger = logging.getLogger("GtkThemes")

        self.themes_path = os.path.expanduser('~/.themes')

        self._themes = self.get_themes_list()

    def _parse_theme(self, theme_path: str):
        with open(theme_path) as file:
            content = file.read().splitlines()
            try:
                gnome_metatheme = content.index('[X-GNOME-Metatheme]') + 1
            except ValueError:
                self.logger.error(f'Could not find [X-GNOME-Metatheme] in {theme_path}.')
                return ''
            return content[gnome_metatheme].split('=')[1]
    

    def get_themes_list(self):
        themes = Gtk.StringList.new([])
        for x in glob(self.themes_path + "/**/index.theme", recursive=True):
            if (n:= self._parse_theme(x)) != '':
                themes.append(n)
        return themes
    
    def set_theme(self, theme):
        self.set_string('gtk-theme', theme)

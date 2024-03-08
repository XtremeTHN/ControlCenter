from gi.repository import Gtk, Gio, GObject
from modules.config import GtkConfig
from glob import glob

import os
import logging

def set_margins(widget: Gtk.Widget, margins: list[int]):
    """
        Reminder: margins = [top, right, bottom, left]
    """
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

class ThemeParser:
    def __init__(self, file) -> None:
        self.file = file
        self.logger = logging.getLogger('ThemeParser')
    
    def _parse_section(self, section_pos, file_content):
        # key = value
        values = {}

        for line in file_content[section_pos:]:
            if line.startswith('#') or line == '':
                continue
            elif not line.startswith('['):
                key, value = line.split('=')
                values[key] = value
            else:
                break
        
        return values

    def parse(self) -> dict:
        self.logger.debug('Parsing theme file: %s', self.file)

        with open(self.file) as file:
            contents = file.read().splitlines()
            conf = {}
            
            for index, line in enumerate(contents):
                if line.startswith('#') or line == '':
                    continue
                else:
                    if line.startswith('[') and line.endswith(']'):
                        conf[line[1:-1]] = self._parse_section(index + 1, contents)
        
            return conf

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
        theme = ThemeParser(theme_path).parse()
        if (n:=theme.get('Desktop Entry')) is not None:
            if n.get('Type') == "X-GNOME-Metatheme":
                return os.path.basename(os.path.split(theme_path)[0])
            else:
                self.logger.error(f'Could not find Desktop Entry Type in {theme_path}')
        else:
            self.logger.error(f'Could not find [X-GNOME-Metatheme] in {theme_path}')
            return
    

    def get_themes_list(self):
        themes = Gtk.StringList.new([])
        for x in glob(self.themes_path + "/**/index.theme", recursive=True):
            if (n:= self._parse_theme(x)) is not None:
                themes.append(n)
        return themes
    
    def set_theme(self, theme):
        self.set_string('gtk-theme', theme)

    def get_current_color_scheme(self):
        return self.get_string('color-scheme')
    
    def set_current_color_scheme(self, color_scheme):
        self.set_string('color-scheme', color_scheme)

class ScrolledBox(Gtk.ScrolledWindow):
    def __init__(self, **box_args):
        self.box = Gtk.Box(spacing=10, orientation=Gtk.Orientation.VERTICAL, **box_args)
        super().__init__(child=self.box)
    
    def apppends(self, *widgets):
        for widget in widgets:
            self.box.append(widget)

    def append(self, widget):
        self.box.append(widget)

class GtkIconTheme(GtkConfig):
    def __init__(self):
        GtkConfig.__init__(self)
        self.logger = logging.getLogger('GtkIconTheme')

    def _parse_icon_theme(self, file):
        
        icon_theme = ThemeParser(file).parse()
        if (n:=icon_theme.get('Icon Theme')) is not None:
            if n.get('Name') is not None:
                return n['Name']
        else:
            self.logger.error(f'Could not find icon theme name in {file}.')
            return

    def get_icons(self):
        icon_paths = ['/usr/share/icons']
        icon_list = Gtk.StringList.new([])

        for x in glob(icon_paths[0] + "/**/index.theme", recursive=True):
            if os.path.exists(os.path.join(os.path.split(x)[0], 'cursor.theme')):
                continue
            if (n:= self._parse_icon_theme(x)) is not None:
                icon_list.append(n)
        
        return icon_list

    def get_current_icon_theme(self):
        return self.get_string('icon-theme')

    def set_icon_theme(self, icon_theme_name):
        self.set_string('icon-theme', icon_theme_name)

class GtkCursorTheme(GtkConfig):
    def __init__(self):
        super().__init__()

        self.logger = logging.getLogger('GtkCursorTheme')

    def get_cursors(self):
        cursor_paths = ['/usr/share/icons', os.path.expanduser('~/.icons')]
        cursor_list = Gtk.StringList.new([])

        for x in glob(cursor_paths[0] + "/**/cursor.theme", recursive=True):
            if (n:= self._parse_cursor_theme(x)) is not None:
                cursor_list.append(n)
        
        return cursor_list

    def _parse_cursor_theme(self, file):
        cursor_theme = ThemeParser(file).parse()
        if (n:=cursor_theme.get('Icon Theme')) is not None:
            if n.get('Name') is not None:
                return n['Name']
        else:
            self.logger.error(f'Could not find cursor theme name in {file}.')
            return
    
    def set_default_cursor_theme(self, cursor_theme: str):
        self.set_string('cursor-theme', cursor_theme)
    
    def get_default_cursor_theme(self):
        return self.get_string('cursor-theme')

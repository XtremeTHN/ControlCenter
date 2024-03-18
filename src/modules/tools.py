from gi.repository import Adw, Gtk, Gio, GObject
from modules.config import GtkConfig, AppearanceConfig
from glob import glob

import os
import logging

def create_header():
    sidebar_toolbar = Adw.ToolbarView.new()
    sidebar_header = Adw.HeaderBar.new()
    sidebar_toolbar.add_top_bar(sidebar_header)
    return sidebar_toolbar, sidebar_header

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
    
def create_empty_file(file: str):
    open(file, 'a').close()

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
        self.box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, **box_args)
        super().__init__(child=self.box, hscrollbar_policy=Gtk.PolicyType.NEVER, vscrollbar_policy=Gtk.PolicyType.AUTOMATIC)
    
    def apppends(self, *widgets):
        for widget in widgets:
            self.box.append(widget)

    def append(self, widget):
        self.box.append(widget)


class ConfigPage(ScrolledBox):
    def __init__(self, logger_name=None, **box_args):
        self.logger = logging.getLogger(logger_name if logger_name is not None else "ConfigPage")
        super().__init__(**box_args)
    
    def create_new_group(self, title, description, suffix=None, append=True):
        group = Adw.PreferencesGroup(title=title, description=description)
        if suffix is not None:
            if isinstance(suffix, Gtk.Widget):
                group.set_header_suffix(suffix=suffix)
            else:
                self.logger.warning("The provided suffix widget is not an instance of Gtk.Widget, fix it pls, or remove this verification")
                self.logger.warning("Ignoring suffix...")

        listbox_actions = Gtk.ListBox.new()
        listbox_actions.set_selection_mode(Gtk.SelectionMode.NONE)
        listbox_actions.get_style_context().add_class('boxed-list')
        
        group.add(listbox_actions)
        if append is True:
            self.append(group)
            return listbox_actions
        else:
            return group, listbox_actions
    
    def set_default_selected_on_combo_row(self, comborow: Adw.ComboRow, condition):
        model = comborow.get_model()
        for x in range(0, model.get_n_items()):
            if model.get_item(x).get_string() == condition:
                comborow.set_selected(x)


class GtkIconTheme(GtkConfig):
    def __init__(self):
        GtkConfig.__init__(self)
        self.logger = logging.getLogger('GtkIconTheme')

    def _parse_icon_theme(self, file):
        
        icon_theme = ThemeParser(file).parse()
        if (n:=icon_theme.get('Icon Theme')) is not None:
            if n.get('Directories') is not None:
                if n.get('Name') is not None:
                    return n['Name']
                else: 
                    self.logger.warning("No name has been found on %s", file)
                    return
            else:
                self.logger.warning("%s is not an icon theme", file)
                return
        else:
            self.logger.error(f'Could not find icon theme name in {file}.')
            return

    def get_icons(self):
        self.logger.info("Finding icons...")
        icon_paths = ['/usr/share/icons', os.path.expanduser("~/.icons"), os.path.expanduser("~/.local/share/icons/")]
        icon_list = Gtk.StringList.new([])

        exclusions = ["default", "hicolor", "locolor"]
        
        for dir in icon_paths:
            for x in glob(dir + "/**/index.theme", recursive=True):
                if os.path.exists(os.path.join(os.path.split(x)[0], 'cursor.theme')):
                    continue
                if os.path.basename(os.path.split(x)[0]) not in exclusions:
                    if (n:= self._parse_icon_theme(x)) is not None:
                        icon_list.append(n)
                else:
                    self.logger.debug("Icon theme is in exclusion list")
        
        return icon_list

    def get_current_icon_theme(self):
        return self.get_string('icon-theme') 

    def set_icon_theme(self, icon_theme_name):
        self.set_string('icon-theme', icon_theme_name)

class GtkCursorTheme(GtkConfig):
    def __init__(self):
        super().__init__()
        self.appearance_conf = AppearanceConfig()

        self.logger = logging.getLogger('GtkCursorTheme')

    def get_cursors(self):
        cursor_paths = ['/usr/share/icons', os.path.expanduser('~/.icons')]
        cursor_list = Gtk.StringList.new([])
        for path in cursor_paths:
            for x in glob(path + "/**/cursor.theme", recursive=True):
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

    def set_default_cursor_size(self, size: int):
        self.set_int('cursor-size', size)
    
    def get_default_cursor_theme(self):
        return self.get_string('cursor-theme')

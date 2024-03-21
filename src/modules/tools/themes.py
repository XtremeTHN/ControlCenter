import logging
import os

from glob import glob
from modules.config import AppearanceConfig, GtkConfig
from gi.repository import Gtk, GObject

class ThemeParser:
    def __init__(self, file) -> None:
        """
        Parses a theme file (index.theme)
        Could be an Gtk Theme, cursor theme, icon theme, etc.
        Implement a filter to identificate which of this types is your file

        Args:
            file (str): The file path
        """
        self.file = file
        self.logger = logging.getLogger('ThemeParser')
    
    def _parse_section(self, section_pos, file_content):
        """Parses a theme file section

        Args:
            section_pos (int): The line number wheres the section is located
            file_content (str): The theme file content

        Returns:
            dict[str, str]: A dict containing the values of the theme file
        """
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
        """Parses the theme file

        Returns:
            dict: All of the theme file values but in a python dictionary
        """
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

class GtkThemes(GtkConfig, GObject.GObject):
    def __init__(self):
        """
        A class that makes easier the themes finding and setting
        Derives from GtkConfig
        """
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
        """Gets all installed gtk themes

        Returns:
            Gtk.StringList: A string list containing the name of the themes
        """
        themes = Gtk.StringList.new([])
        for x in glob(self.themes_path + "/**/index.theme", recursive=True):
            if (n:= self._parse_theme(x)) is not None:
                themes.append(n)
        return themes
    
    def set_theme(self, theme):
        """Sets the gtk theme
        Modifies the org.gnome.desktop.interface.gtk-theme setting

        Args:
            theme (str): The theme name you want to set
        """
        self.set_string('gtk-theme', theme)

    def get_current_color_scheme(self):
        """Gets the current colorscheme

        Returns:
            str: The current selected colorscheme. Could be "default", "prefer-dark", "prefer-light"
        """
        return self.get_string('color-scheme')
    
    def set_current_color_scheme(self, color_scheme):
        """Sets the current colorscheme

        Args:
            color_scheme (str): The colorscheme you want to set. Needs to be "default", "prefer-dark" or "prefer-light"
        """
        if color_scheme not in ["default", "prefer-dark", "prefer-light"]:
            self.logger.warning("Invalid color scheme. %s", color_scheme)
        self.set_string('color-scheme', color_scheme)

class GtkIconTheme(GtkConfig):
    def __init__(self):
        """A class that makes easier the icon theme finding, getting, and setting
        """
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
        """Gets a string list of current installed icon themes.
        It excludes the following icon themes: default, hicolor, locolor

        Returns:
            Gtk.StringList: A string list containing all installed icon themes
        """
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
        """Gets the current icon theme

        Returns:
            str: The current icon theme
        """
        return self.get_string('icon-theme') 

    def set_icon_theme(self, icon_theme_name):
        """Gets the current icon theme
        Modifies org.gnome.desktop.interface.icon-theme

        Args:
            icon_theme_name (str): The icon theme that will be selected
        """
        self.set_string('icon-theme', icon_theme_name)

class GtkCursorTheme(GtkConfig):
    def __init__(self):
        """A class that makes easier the finding, getting and setting the gtk cursor theme
        """
        super().__init__()
        self.appearance_conf = AppearanceConfig()

        self.logger = logging.getLogger('GtkCursorTheme')

    def get_cursors(self):
        """Gets a string list of current installed cursor themes

        Returns:
            Gtk.StringList: A string list containing the installed cursor themes
        """
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
        """Sets the default cursor theme
        Modifies org.gnome.desktop.interface.cursor-theme

        Args:
            cursor_theme (str): The cursor theme that will be setted
        """
        self.set_string('cursor-theme', cursor_theme)

    def set_default_cursor_size(self, size: int):
        """Sets the default cursor size
        Modifies org.gnome.desktop.interface.cursor-size

        Args:
            size (int): The cursor size
        """
        self.set_int('cursor-size', size)
    
    def get_default_cursor_theme(self):
        """Gets the default cursor theme

        Returns:
            str: The cursor theme
        """
        return self.get_string('cursor-theme')
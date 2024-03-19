from gi.repository import Adw, Gtk, Gio, GObject
from modules.config import GtkConfig, AppearanceConfig
from glob import glob

import os
import logging

def create_header():
    """
    Creates a header
    
    Returns:
        tuple(Adw.ToolBarView, Adw.HeaderBar): a Adw.ToolBar containing the header, and the header widget
    """
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
    """
    Opens a file, reads it, and return it's contents.
    It uses Gio.File for reading the file.

    Args:
        file (str): The file path

    Returns:
        str: The contents of the file
    """
    gfile = Gio.File.new_for_path(file)
    if gfile.query_exists() is not False:
        return gfile.load_contents(None)[1].decode('utf-8')
    else:
        return ""

def include_bytes(file: str) -> bytes:
    """
    Same to include_file but instead of a string returns bytes

    Args:
        file (str): The file path

    Returns:
        bytes: The contents of the file in bytes
    """
    gfile = Gio.File.new_for_path(file)
    return gfile.load_contents(None)[1]
    
def create_empty_file(file: str):
    """
    Creates an empty file

    Args:
        file (str): The file path
    """
    open(file, 'a').close()

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

class HBox(Gtk.Box):
    def __init__(self, spacing=10, **extra):
        """An Gtk.Box but with the orientation in horizontal, it adds a new function to add more than one widget in a single call

        Args:
            spacing (int, optional): The space that will be between the widgets. Defaults to 10.
        """
        super().__init__(orientation=Gtk.Orientation.HORIZONTAL, spacing=spacing, **extra)
    
    def appends(self, *widgets):
        """Appends more than one widgets
        
        Args:
            *widgets: All the widgets you want to append
        """
        for widget in widgets:
            self.append(widget)

class VBox(Gtk.Box):
    def __init__(self, spacing=10, **extra):
        """Same as the HBox but in vertical

        Args:
            spacing (int, optional): The space that will be between the widgets. Defaults to 10.
        """
        super().__init__(orientation=Gtk.Orientation.VERTICAL, spacing=spacing, **extra)
    
    def appends(self, *widgets):
        """Appends more than one widgets
        
        Args:
            *widgets: All the widgets you want to append
        """
        for widget in widgets:
            self.append(widget)

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

class ScrolledBox(Gtk.ScrolledWindow):
    def __init__(self, **box_args):
        """A Gtk.ScrolledWindow but with an integrated box
        """
        self.box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, **box_args)
        super().__init__(child=self.box, hscrollbar_policy=Gtk.PolicyType.NEVER, vscrollbar_policy=Gtk.PolicyType.AUTOMATIC)
    
    def apppends(self, *widgets):
        """Appends more than one widgets to the integrated box
        
        Args:
            *widgets (list[Gtk.Widget]): All the widgets you want to append
        """
        for widget in widgets:
            self.box.append(widget)

    def append(self, widget):
        """Appends one widget to the integrated box

        Args:
            widget (Gtk.Widget): The gtk widget
        """
        self.box.append(widget)


class ConfigPage(VBox):
    def __init__(self, logger_name=None, **box_args):
        """A class that makes easier the creation of new pages of the control center

        Args:
            logger_name (str, optional): The logger name. Defaults to None.
        """
        self.logger = logging.getLogger(logger_name if logger_name is not None else "ConfigPage")
        super().__init__(spacing=2)
        
        self.toolbar, self.header = create_header()

        self.scroll_box = ScrolledBox(vexpand=True, **box_args)
        set_margins(self.scroll_box, [10])
        
        self.appends(self.toolbar, self.scroll_box)
    
    def create_new_group(self, title, description, suffix=None, append=True):
        """Creates a new group and appends it to the ScrolledBox

        Args:
            title (str): The Adw.PreferencesGroup title
            description (str): The Adw.PreferencesGroup description
            suffix (Gtk.Widget, optional): A widget that will be placed to the end. Unused. Defaults to None.
            append (bool, optional): Should the Adw.PreferencesGroup will be added to the ScrolledBox. Defaults to True.

        Returns:
            Gtk.ListBox | tuple(Adw.PreferencesGroup, Gtk.ListBox): A listbox containing all of the configurations. If append is False, then the PreferencesGroup will also be returned
        """
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
            self.scroll_box.append(group)
            return listbox_actions
        else:
            return group, listbox_actions
    
    def set_default_selected_on_combo_row(self, comborow: Adw.ComboRow, condition):
        """Sets the selected item on the target comborow.
        It checks if any of the model childs equals to the condition argument

        Args:
            comborow (Adw.ComboRow): The target comborow
            condition (str): The str that will be selected
        """
        model = comborow.get_model()
        for x in range(0, model.get_n_items()):
            if model.get_item(x).get_string() == condition:
                comborow.set_selected(x)


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

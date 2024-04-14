import logging
import os

from modules.config import GtkConfig

from modules.tools.themes import GtkThemes, GtkIconTheme, GtkCursorTheme
from modules.tools.custom_widgets import ConfigPage, InfoRow, ErrorDialog
from modules.tools.utilities import set_margins

from modules.tools.wallpapers import Wallpapers

from modules.hyprland.ctl import HyprCtl

from gi.repository import Gtk, GObject, Adw, Gio, GLib

class GtkAppearanceConfig(ConfigPage):
    ICON_VIEW_ICONS=[
        "user-home",
		"user-desktop",
		"folder",
		"folder-remote",
		"user-trash",
		"x-office-document",
		"application-x-executable",
		"image-x-generic",
		"package-x-generic",
		"emblem-mail",
		"utilities-terminal",
		"chromium",
		"firefox",
		"gimp"
    ]
    def __init__(self):
        super().__init__("AppearancePage > GtkAppearanceConfig", header=False, spacing=20)
        
        self.config = GtkConfig()

        self.gtk_themes = GtkThemes()
        self.ctl = HyprCtl()

        style_group_listbox_actions = self.create_new_group("Style of widgets", "Customize the appearance of Gtk widgets")

        # Gtk Theme
        gtk_theme_model = self.gtk_themes.get_themes_list()
        gtk_theme = Adw.ComboRow(model=gtk_theme_model, title="GTK theme", subtitle="Global gtk theme (from ~/.themes)")
        
        self.set_default_selected_on_combo_row(gtk_theme, self.gtk_themes.get_string('gtk-theme'))

        gtk_theme.connect('notify::selected', self.on_theme_selected)

        style_group_listbox_actions.append(gtk_theme)
        # End Gtk Theme

        # Color scheme
        gtk_color_scheme = Adw.ComboRow(title="GTK color scheme", subtitle="Global gtk color scheme")
        gtk_color_scheme.set_model(Gtk.StringList.new(['default', 'prefer-light', 'prefer-dark']))
        
        self.set_default_selected_on_combo_row(gtk_color_scheme, self.gtk_themes.get_string('color-scheme'))
        
        gtk_color_scheme.connect('notify::selected', self.on_color_scheme_changed)

        style_group_listbox_actions.append(gtk_color_scheme)
        # End Color scheme

        # Font
        font_config = Adw.ExpanderRow(title="Font", subtitle="Customize the font and font size")

        default_font = Adw.EntryRow(title="Font name", text=self.gtk_themes.font_value[0]) 
        default_font_size = Adw.SpinRow(adjustment=Gtk.Adjustment(value=int(self.gtk_themes.font_value[1]), step_increment=1, lower=0, upper=72), title="Font size")

        default_font.connect('changed', self.on_default_font_changed)
        default_font_size.connect('notify::value', self.on_default_font_size_changed)

        font_config.add_row(default_font)
        font_config.add_row(default_font_size)

        style_group_listbox_actions.append(font_config)
        # End Font
        
        # Icons
        icon_theme_listbox_actions = self.create_new_group("Icon theme", "Set and visualize the icon theme!")
        
        self.icon_themes = GtkIconTheme()

        icon_themes_combo = Adw.ComboRow(model=self.icon_themes.get_icons(), title="Global icon theme", subtitle="Set the global icon theme by choosing it from the combobox")
        icon_themes_combo.connect('notify::selected', self.on_icon_theme_changed)
        
        icon_theme_listbox_actions.append(icon_themes_combo)
        self.set_default_selected_on_combo_row(icon_themes_combo, self.icon_themes.get_current_icon_theme())

        # End Icons

        # Preview Icon
        icons_preview_row = Adw.ActionRow(subtitle="Preview icons in the current theme")
        icons_flow_box = Gtk.FlowBox.new()
        
        set_margins(icons_flow_box, [10])

        for x in self.ICON_VIEW_ICONS:
            icon = Gtk.Image.new_from_icon_name(x)
            icon.set_icon_size(Gtk.IconSize.LARGE)
            icons_flow_box.append(icon)

        icons_preview_row.set_child(icons_flow_box)

        icon_theme_listbox_actions.append(icons_preview_row)
        # End Preview Icon

        # Cursor
        self.cursors = GtkCursorTheme()

        cursor_theme_listbox_actions = self.create_new_group("Cursor theme", "Set and visualize the cursor theme!")

        self.cursor_theme_combo = Adw.ComboRow(model=self.cursors.get_cursors(), title="Global cursor theme", subtitle="Set the global cursor theme by choosing it from the combobox")

        self.set_default_selected_on_combo_row(self.cursor_theme_combo, self.cursors.get_default_cursor_theme())
        
        cursor_theme_listbox_actions.append(self.cursor_theme_combo)
        
        cursor_size_adjustment = Gtk.Adjustment(step_increment=1, upper=255, lower=4)
        self.cursor_size = Adw.SpinRow(adjustment=cursor_size_adjustment, title="Cursor size")
        
        self.cursor_size.connect("notify::value", self.on_cursor_size_changed)
        self.cursor_theme_combo.connect('notify::selected', self.on_cursor_theme_changed)
        
        self.cursors.bind_config('cursor-size', self.cursor_size, "value")
        
        cursor_theme_listbox_actions.append(self.cursor_size)

    def on_icon_theme_changed(self, combo_row: Adw.ComboRow, *argv):
        self.icon_themes.set_icon_theme(str(combo_row.get_selected_item().get_string()))
            
    def on_color_scheme_changed(self, combo_row: Adw.ComboRow, *argv):
        self.gtk_themes.set_current_color_scheme(combo_row.get_selected_item().get_string())
    
    def on_default_font_changed(self, entry, *argv):
        self.gtk_themes.set_font_name(entry.get_text())
    
    def on_default_font_size_changed(self, spin, *argv):
        self.gtk_themes.set_font_size(int(spin.get_value()))
    
    def on_cursor_theme_changed(self, combo_row: Adw.ComboRow, *argv):
        cursor = combo_row.get_selected_item().get_string()
        self.cursors.set_default_cursor_theme(cursor)
        self.ctl.setCursor(cursor, int(self.cursor_size.get_value()))

    def on_cursor_size_changed(self, spin, *argv):
        selected_item = self.cursor_theme_combo.get_selected_item()
        if selected_item is not None:
            self.ctl.setCursor(selected_item.get_string(), int(spin.get_value()))
        else:
            self.logger.warning("Theres no selected item on cursor size spin widget")
    
    def on_theme_selected(self, combo_row: Adw.ComboRow, _):
        theme = combo_row.get_selected_item()
        self.gtk_themes.set_theme(theme.get_string())

class WallpaperItem(Gtk.Picture):
    def __init__(self, image_path: str):
        self.image_file = Gio.File.new_for_path(image_path)
        super().__init__(file=self.image_file, content_fit=Gtk.ContentFit.COVER, can_shrink=True, css_classes=["card"])
        self.set_size_request(0,160)

class WallpapersPage(ConfigPage):
    def __init__(self, window: Gtk.Window):
        super().__init__(logger_name="AppearancePage > WallpapersPage", header=False, spacing=20)
        
        self.window = window

        self.scroll_box.set_policy(Gtk.PolicyType.NEVER, Gtk.ScrollablePolicy.NATURAL)
        
        self.wall_obj = Wallpapers()
        self.wall_backend = self.wall_obj.get_backend()
        
        self.current_wallpaper_group = self.create_new_group("Current wallpaper", "")
                
        self.current_wallpaper_widget = WallpaperItem(self.wall_backend.get_wallpaper())

        self.current_wallpaper_group.append(self.current_wallpaper_widget)

        wallpaper_chooser = Gtk.Button.new()
        wallpaper_chooser_content = Adw.ButtonContent(icon_name="document-open-symbolic", label="Choose a wallpaper")
        wallpaper_chooser.set_child(wallpaper_chooser_content)

        wallpaper_chooser.connect("clicked", self.choose_file)

        self.scroll_box.append(wallpaper_chooser)

        self.backend_info_group = self.create_new_group("Wallpaper backend info", "Information about the current wallpaper backend (swww, swaybg, hyprwall, etc.)")

        self.wallpaper_name = InfoRow("Current wallpaper path", self.wall_backend.get_wallpaper())

        self.wall_backend.connect('changed', self.on_wall_backend_prop_changed)
        self.backend_info_group.append(InfoRow("Version", self.wall_backend.get_version()))
        self.backend_info_group.append(self.wallpaper_name)
    
    def on_wallpaper_choosen(self, flow: Gtk.FlowBox, child: Gtk.FlowBoxChild):
        picture: Gio.File = child.get_child().get_file()
        self.wall_backend.set_wallpaper(picture.get_path())

    def choose_file(self, button):
        def on_response(src_obj: Gtk.FileDialog, result: Gio.AsyncResult):
            try:
                file = src_obj.open_finish(result)
            except Exception as e:
                if (n:=" ".join(e.args)) != "Dismissed by user":
                    ErrorDialog(text=n, title="Error", actions={"close": {"label": "Close"}}, window=self.window)
                    return
            else:
                try:
                    self.wall_backend.set_wallpaper(file.get_path())
                except Exception as e:
                    ErrorDialog(text=e, title="Error", actions={"close": {"label": "Close"}}, window=self.window)
                    return
                self.on_wall_backend_prop_changed(None)
                
        dialog = Gtk.FileDialog(modal=True, title="Choose a wallpaper")
        dialog.open(self.window, None, on_response)
    
    def on_wall_backend_prop_changed(self, _):
        wall = self.wall_backend.get_wallpaper()

        file = Gio.File.new_for_path(wall)
        self.wallpaper_name.set_subtitle(wall)

        self.current_wallpaper_widget.set_file(file)
        
class AppearancePage(ConfigPage):
    def __init__(self, window):
        super().__init__(logger_name="AppearancePage", add_scroll_box=False, spacing=20)
        
        self.view_switcher = Adw.ViewSwitcher(policy=Adw.ViewSwitcherPolicy.WIDE, vexpand=False)
        self.view_switcher_stack = Adw.ViewStack()
        
        self.gtk_appearance_config = GtkAppearanceConfig()
        
        self.view_switcher_stack.add_titled_with_icon(self.gtk_appearance_config, "gtkconfig-page", "Gtk Config", "applications-system-symbolic")
        
        self.desktop_appearance_config = WallpapersPage(window)
        
        self.view_switcher_stack.add_titled_with_icon(self.desktop_appearance_config, "wallpapers-page", "Wallpapers", "preferences-system-symbolic")
        
        self.view_switcher.set_stack(self.view_switcher_stack)
        self.header.set_title_widget(self.view_switcher)
        
        self.append(self.view_switcher_stack)
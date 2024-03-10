import logging

from modules.config import AppearanceConfig, GtkConfig
from modules.tools import GtkThemes, GtkIconTheme, GtkCursorTheme, ScrolledBox, HBox, set_margins
from modules.hyprland.ctl import HyprCtl

from gi.repository import Gtk, GObject, Adw, Gio, GLib


class AppearancePage(ScrolledBox):
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
        super().__init__()
        
        self.config = GtkConfig()
        self.logger = logging.getLogger('AppearancePage')

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

        for x in self.ICON_VIEW_ICONS:
            icon = Gtk.Image.new_from_gicon(Gio.ThemedIcon.new(x))
            icon.set_icon_size(Gtk.IconSize.LARGE)
            icons_flow_box.append(icon)

        icons_preview_row.set_child(icons_flow_box)

        icon_theme_listbox_actions.append(icons_preview_row)
        # End Preview Icon

        # Cursor
        self.cursors = GtkCursorTheme()

        cursor_theme_listbox_actions = self.create_new_group("Cursor theme", "Set and visualize the cursor theme!")

        cursor_theme_combo = Adw.ComboRow(model=self.cursors.get_cursors(), title="Global cursor theme", subtitle="Set the global cursor theme by choosing it from the combobox")
        cursor_theme_combo.connect('notify::selected', self.on_cursor_theme_changed)

        self.set_default_selected_on_combo_row(cursor_theme_combo, self.cursors.get_default_cursor_theme())
        
        cursor_theme_listbox_actions.append(cursor_theme_combo)
        
        cursor_size_adjustment = Gtk.Adjustment(step_increment=1, upper=255, lower=4)
        cursor_size = Adw.SpinRow(adjustment=cursor_size_adjustment, title="Cursor size")
        
        self.cursors.bind_config('cursor-size', cursor_size, "value")
        
        cursor_theme_listbox_actions.append(cursor_size)

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
        self.ctl.setCursor(cursor, 24)

    def on_theme_selected(self, combo_row: Adw.ComboRow, _):
        theme = combo_row.get_selected_item()
        self.gtk_themes.set_theme(theme.get_string())

    def create_new_group(self, title, description, suffix=None):
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
        self.append(group)
        return listbox_actions
    
    def set_default_selected_on_combo_row(self, comborow: Adw.ComboRow, condition):
        model = comborow.get_model()
        for x in range(0, model.get_n_items()):
            if model.get_item(x).get_string() == condition:
                comborow.set_selected(x)

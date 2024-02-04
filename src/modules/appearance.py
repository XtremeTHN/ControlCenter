from modules.config import AppearanceConfig
from modules.tools import GtkThemes, VBox, HBox, set_margins

from gi.repository import Gtk, GObject, Adw, Gio


class AppearancePage(VBox):
    def __init__(self):
        # AppearanceConfig.__init__(self)
        super().__init__(spacing=10)

        self.gtk_themes = GtkThemes()
        
        reload_button = Gtk.Button.new_from_icon_name("view-refresh-symbolic")
        reload_button.set_halign(Gtk.Align.CENTER)

        reload_button.connect('clicked', self.reload_themes_model)

        style_group = Adw.PreferencesGroup(title="Style", description="Customize the appearance of Gtk and some other stuff")
        style_group.set_header_suffix(reload_button)
        style_group_listbox_actions = Gtk.ListBox.new()
        style_group_listbox_actions.set_selection_mode(Gtk.SelectionMode.NONE)
        style_group_listbox_actions.get_style_context().add_class('boxed-list')


        self.gtk_theme = Adw.ComboRow(title="GTK theme", subtitle="Global gtk theme (from ~/.themes)")
        self.gtk_theme.set_model(self.gtk_themes._themes)

        self.gtk_theme.connect('notify::selected', self.change_theme)
        style_group_listbox_actions.append(self.gtk_theme)

        style_group.add(style_group_listbox_actions)

        self.append(style_group)

    def reload_themes_model(self, _):
        self.gtk_theme.set_model(self.gtk_themes.get_themes_list())
        
    def change_theme(self, combo_row: Adw.ComboRow, _):
        theme: Gtk.StringObject = self.gtk_themes._themes.get_item(combo_row.get_selected())
        self.gtk_themes.set_theme(theme.get_string())
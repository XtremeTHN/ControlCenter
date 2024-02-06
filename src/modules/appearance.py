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

        style_group = Adw.PreferencesGroup(title="Style of widgets", description="Customize the appearance of Gtk widgets")
        style_group.set_header_suffix(reload_button)
        style_group_listbox_actions = Gtk.ListBox.new()
        style_group_listbox_actions.set_selection_mode(Gtk.SelectionMode.NONE)
        style_group_listbox_actions.get_style_context().add_class('boxed-list')

        # Gtk Theme
        self.gtk_theme = Adw.ComboRow(title="GTK theme", subtitle="Global gtk theme (from ~/.themes)")
        self.gtk_theme.set_model(self.gtk_themes._themes)

        self.gtk_theme.connect('notify::selected', self.change_theme)

        style_group_listbox_actions.append(self.gtk_theme)
        # End Gtk Theme

        # Color scheme
        gtk_color_scheme = Adw.ComboRow(title="GTK color scheme", subtitle="Global gtk color scheme")
        gtk_color_schemes = Gtk.StringList.new(['default', 'prefer-light', 'prefer-dark'])
        gtk_color_scheme.set_model(gtk_color_schemes)
        
        for x in range(0, gtk_color_schemes.get_n_items()):
            if gtk_color_schemes.get_item(x).get_string() == self.gtk_themes.get_string('color-scheme'):
                gtk_color_scheme.set_selected(x)
        
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
        self.icon_theme_group = Adw.PreferencesGroup(title="Icons", description="Customize the icons")

        style_group.add(style_group_listbox_actions)
        self.append(style_group)
    
    def on_color_scheme_changed(self, combo_row: Adw.ComboRow, *argv):
        self.gtk_themes.set_current_color_scheme(str(combo_row.get_model().get_item(combo_row.get_selected()).get_string()))
    
    def on_default_font_changed(self, entry, *argv):
        self.gtk_themes.set_font_name(entry.get_text())
    
    def on_default_font_size_changed(self, spin, *argv):
        self.gtk_themes.set_font_size(int(spin.get_value()))

    def reload_themes_model(self, _):
        self.gtk_theme.set_model(self.gtk_themes.get_themes_list())
        
    def change_theme(self, combo_row: Adw.ComboRow, _):
        theme: Gtk.StringObject = self.gtk_themes._themes.get_item(combo_row.get_selected())
        self.gtk_themes.set_theme(theme.get_string())
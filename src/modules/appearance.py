import logging

from modules.config import AppearanceConfig
from modules.tools import GtkThemes, GtkIconTheme, VBox, HBox, set_margins

from gi.repository import Gtk, GObject, Adw, Gio


class AppearancePage(VBox):
    def __init__(self):
        # AppearanceConfig.__init__(self)
        super().__init__(spacing=10)
        self.logger = logging.getLogger('AppearancePage')

        self.gtk_themes = GtkThemes()
        
        reload_button = Gtk.Button.new_from_icon_name("view-refresh-symbolic")
        reload_button.set_halign(Gtk.Align.CENTER)

        reload_button.connect('clicked', self.reload_themes_model)

        style_group_listbox_actions = self.create_new_group("Style of widgets", "Customize the appearance of Gtk widgets", suffix=reload_button)

        # Gtk Theme
        self.gtk_theme = Adw.ComboRow(title="GTK theme", subtitle="Global gtk theme (from ~/.themes)")
        self.gtk_theme.set_model(self.gtk_themes._themes)

        self.gtk_theme.connect('notify::selected', self.change_theme)

        style_group_listbox_actions.append(self.gtk_theme)
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

        self.set_default_selected_on_combo_row(icon_themes_combo, self.icon_themes.get_current_icon_theme())

        icon_theme_listbox_actions.append(icon_themes_combo)
    
    def on_icon_theme_changed(self, combo_row: Adw.ComboRow, *argv):
        self.icon_themes.set_icon_theme(str(combo_row.get_selected_item().get_string()))
            
    def on_color_scheme_changed(self, combo_row: Adw.ComboRow, *argv):
        self.gtk_themes.set_current_color_scheme(combo_row.get_selected_item().get_string())
    
    def on_default_font_changed(self, entry, *argv):
        self.gtk_themes.set_font_name(entry.get_text())
    
    def on_default_font_size_changed(self, spin, *argv):
        self.gtk_themes.set_font_size(int(spin.get_value()))

    def reload_themes_model(self, _):
        self.gtk_theme.set_model(self.gtk_themes.get_themes_list())
        
    def change_theme(self, combo_row: Adw.ComboRow, _):
        theme: Gtk.StringObject = self.gtk_themes._themes.get_item(combo_row.get_selected())
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
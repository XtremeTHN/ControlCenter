from gi.repository import Gtk, Adw
from modules.tools.utilities import set_margins

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

class ScrolledBox(Gtk.ScrolledWindow):
    def __init__(self, **box_args):
        """A Gtk.ScrolledWindow but with an integrated box
        """
        self.widget = Adw.Clamp.new()
        self.box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, **box_args)
        set_margins(self.box, [10,5,10,5])
        self.widget.set_child(self.box)

        super().__init__(child=self.widget, hscrollbar_policy=Gtk.PolicyType.NEVER, vscrollbar_policy=Gtk.PolicyType.AUTOMATIC)
    
    def appends(self, *widgets):
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
    def __init__(self, logger_name=None, add_scroll_box=True, header=True, **box_args):
        """A class that makes easier the creation of new pages of the control center

        Args:
            logger_name (str, optional): The logger name. Defaults to None.
        """
        self.logger = logging.getLogger(logger_name if logger_name is not None else "ConfigPage")
        super().__init__(spacing=2)
        
        if header is True:
            self.toolbar, self.header = create_header()
            self.append(self.toolbar)
            
        if add_scroll_box is True:
            self.scroll_box = ScrolledBox(vexpand=True, **box_args)
            self.append(self.scroll_box)
    
    def create_new_group(self, title, description, suffix=None, add_listbox=True, append=True):
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
                
        listbox_actions = None
        if add_listbox is True:
            listbox_actions = Gtk.ListBox.new()
            listbox_actions.set_selection_mode(Gtk.SelectionMode.NONE)
            listbox_actions.add_css_class('boxed-list')
        
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
    
    def append(self, widget):
        """Appends a widget to the VBox containing the Header and the scroll box.
        Use this if you don't want to use ScrolledBox

        Args:
            widget (Gtk.Widget): The widget
        """
        super().append(widget)
    
    def appends(self, *widgets):
        """Appends a list of widgets to the VBox containing the Header and the scroll box.
        Use this if you don't want to use ScrolledBox.
        """
        return super().appends(*widgets)


def InfoRow(title, info):
    """Creates an Information "Row", for the style to be applied, this widget needs to be placed inside a Gtk.ListBox with 

    Args:
        title (str): The title
        info (str): The label that will be at the end of the widget

    Returns:
        ActionRow: An ActionRow with the property class
    """
    return Adw.ActionRow(title=title, subtitle=info, activatable=False, subtitle_selectable=True, css_classes=["property"])

class ErrorDialog:
    def __init__(self, text: str, title: str, actions:dict[str, dict]={}, window: Gtk.Window=None):
        self.widget = Adw.MessageDialog(body=text, body_use_markup=True, heading=title, heading_use_markup=True, transient_for=window, modal=True)
        
        if actions != {}:
            for action_name, action_params in actions.items():
                if (n:=action_params.get("label")) is not None:
                    self.widget.add_response(action_name, n)

                if (n:=action_params.get("response-appearance")) is not None:
                    self.widget.set_response_appearance(action_name, n)
                
                if (n:=action_params.get("defaultResponse")) is not None:
                    self.widget.set_default_response(action_name)
                
                if (n:=action_params.get("closeResponse")) is not None:
                    self.widget.set_close_response(action_name)

        self.widget.present()
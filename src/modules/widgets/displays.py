from gi.repository import Adw, Gtk, GObject
from modules.monitors import Monitors
from modules.tools import ConfigPage, HBox, VBox, set_margins

resolution = Gtk.StringList.new([
    "1920x1080",
    "1856x1392",
    "1792x1344",
    "1680x1050",
    "1440x1050",
    "1440x900",
    "1360x768",
    "1280x1024",
    "1024x600",
    "800x600",
])

def InfoRow(title, subtitle, info):
    box = HBox(spacing=10, homogeneous=True)

    labels_box = VBox(spacing=0)
    
    title_widget =  Gtk.Label(halign=Gtk.Align.START, valign=Gtk.Align.CENTER, hexpand=True, label=f"{title}")
    labels_box.append(title_widget)

    margins = [8, 15, 8, 15]
    if subtitle != "":
        subtitle_widget = Gtk.Label(halign=Gtk.Align.START, valign=Gtk.Align.CENTER, hexpand=True, label=f"{subtitle}", css_classes=["dim-label", "caption"])
        labels_box.append(subtitle_widget)
    else:
        margins = [15, 13, 15, 13]

    box.append(labels_box)

    info_label = Gtk.Label(label=info, halign=Gtk.Align.END, valign=Gtk.Align.CENTER)
    box.append(info_label)

    set_margins(box, margins)
    return box

class Displays(ConfigPage):
    def __init__(self):
        super().__init__(logger_name="Displays", spacing=20)
        self.monitor_obj = Monitors()

        self.current_monitor_id = 0
        
        monitors_group = self.create_new_group("Monitors", "")

        displays_btts_row = Adw.ActionRow()
        displays_btts_box = Gtk.FlowBox(row_spacing=4, column_spacing=4, orientation=Gtk.Orientation.VERTICAL, homogeneous=True, selection_mode=Gtk.SelectionMode.NONE)

        self.monitors_configuration_group_stack = Gtk.Stack(transition_duration=0)

        for monitor in self.monitor_obj.monitors:
            monitor_btt = Gtk.Button(hexpand=True, name=monitor.name)

            monitor_btt.connect("clicked", self.on_monitor_btt_clicked, monitor)

            monitor_btt_content = VBox(spacing=0, hexpand=True)

            monitor_name = Gtk.Label(label=f"<span weight=\"bold\" size=\"larger\">{monitor.name}</span>", use_markup=True)
            monitor_id = Gtk.Label(label=f"<span size=\"smaller\">ID: {monitor.id}</span>", use_markup=True)

            monitor_btt_content.appends(monitor_name, monitor_id)

            monitor_btt.set_child(monitor_btt_content)

            displays_btts_box.append(monitor_btt)

            self.create_monitor_widgets(monitor)
        
        displays_btts_row.set_child(displays_btts_box)
        set_margins(displays_btts_row, [10])

        monitors_group.append(displays_btts_row)
        
        self.append(self.monitors_configuration_group_stack)

    def on_monitor_btt_clicked(self, _, monitor):
        self.current_monitor_id = monitor.id
        self.monitors_configuration_group_stack.set_visible_child_name(monitor.name)

    def create_monitor_widgets(self, monitor):
        main_box = VBox(spacing=10)
        page, monitors_configuration_group = self.create_new_group(f"Monitor {monitor.name}", "", append=False)

        resolution_row = Adw.ComboRow(title="Resolution", subtitle="Set the resolution of the selected monitor", model=resolution)
        self.set_default_selected_on_combo_row(resolution_row, f"{monitor.width}x{monitor.height}")

        monitors_configuration_group.append(resolution_row)

        refresh_rate = Adw.ComboRow(model=Gtk.StringList.new([str(monitor.refreshRate)]), title="Refresh rate", subtitle="Set the refresh rate of the selected monitor")
        monitors_configuration_group.append(refresh_rate)
        
        fractional_scale = Adw.SpinRow.new_with_range(1, 2, 0.1)
        fractional_scale.set_title("Fractional scale")
        fractional_scale.set_subtitle("Set the fractional scale of the selected monitor")
        fractional_scale.set_value(monitor.scale)

        monitors_configuration_group.append(fractional_scale)

        apply_btt = Gtk.Button.new_with_label("Apply configuration")
        apply_btt.connect("clicked", self.apply_config, resolution_row, refresh_rate, fractional_scale, monitor)

        info_page = self.create_info_widgets(monitor)

        main_box.appends(page, apply_btt, info_page)
        self.monitors_configuration_group_stack.add_named(main_box, monitor.name)


    def create_info_widgets(self, monitor):
        info_page, monitor_information_group = self.create_new_group("Information", "", append=False)
        name_row = InfoRow("Name", "", monitor.name)
        monitor_information_group.append(name_row)

        maker_row = InfoRow("Maker", "", monitor.make)
        monitor_information_group.append(maker_row)

        model_row = InfoRow("Model", "", monitor.model)
        monitor_information_group.append(model_row)

        serial_row = InfoRow("Serial", "", monitor.serial)
        monitor_information_group.append(serial_row)

        dpms_row = InfoRow("DPMS", "Display Power Management Signaling", "Enabled" if monitor.dpmsStatus else "Disabled")
        monitor_information_group.append(dpms_row)

        vrr_row = InfoRow("VRR", "Variable Refresh Rate", "Enabled" if monitor.vrr else "Disabled")
        monitor_information_group.append(vrr_row)

        tearing = InfoRow("Actively Tearing", "", "Enabled" if monitor.activelyTearing else "Disabled")
        monitor_information_group.append(tearing)

        return info_page
    
    def apply_config(self, btt, resolution_row: Adw.ComboRow, refresh_rate: Adw.ComboRow, fractional_scale: Adw.SpinRow, monitor):
        mon = self.monitor_obj.monitors[monitor.id]
        
        res = resolution_row.get_selected_item()
        if res is None:
            res = [mon.width, mon.height]
        
        res = res.get_string().split("x")

        refreshRate = refresh_rate.get_selected_item()
        if refreshRate is None:
            refreshRate = mon.refreshRate
        
        refreshRate = float(refreshRate.get_string())

        scale = fractional_scale.get_value()
        
        mon.width = int(res[0])
        mon.height = int(res[1])
        mon.refreshRate = refreshRate
        mon.scale = scale

        self.monitor_obj.save()

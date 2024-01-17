from modules.hyprland.monitors import Monitors
import sys

mon = Monitors()
mon.connect("focusedmon", print)

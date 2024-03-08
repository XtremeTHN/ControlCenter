import threading
import logging
import socket
import os

import subprocess

from gi.repository import GObject, GLib

class HyprctlClass:
    def __init__(self):
        """
        Initialize the object.

        This function executes hyprctl commands.         
        Connects to the Hyprctl socket

        Parameters:
            self (object): The object itself.

        Returns:
            None
        """

    def exec(self, cmd, *args):
        """
        Executes a command with hyprctl.
        Args:
            cmd (str): The command to send.
            *args: Additional arguments to include with the command.

        Returns:
            None
        """
        return subprocess.check_output(args=["hyprctl", cmd, *args])

class BaseHyprlandEventsClass(GObject.GObject):
    __gsignals__ = {
        "workspace": (GObject.SignalFlags.RUN_FIRST, None, (str,)),
        "focusedmon": (GObject.SignalFlags.RUN_FIRST, None, (str, str)),
        "activewindow": (GObject.SignalFlags.RUN_FIRST, None, (str, str)),
        "fullscreen": (GObject.SignalFlags.RUN_FIRST, None, (str,)),
        "monitorremoved": (GObject.SignalFlags.RUN_FIRST, None, (str,)),
        "monitoradded": (GObject.SignalFlags.RUN_FIRST, None, (str,)),
        "createworkspace": (GObject.SignalFlags.RUN_FIRST, None, (str,)),
        "destroyworkspace": (GObject.SignalFlags.RUN_FIRST, None, (str,)),
        "moveworkspace": (GObject.SignalFlags.RUN_FIRST, None, (str, str)),
        "activelayout": (GObject.SignalFlags.RUN_FIRST, None, (str, str)),
        "openwindow": (GObject.SignalFlags.RUN_FIRST, None, (str, str, str, str)),
        "closewindow": (GObject.SignalFlags.RUN_FIRST, None, (str,)),
        "movewindow": (GObject.SignalFlags.RUN_FIRST, None, (str, str)),
        "openlayer": (GObject.SignalFlags.RUN_FIRST, None, (str,)),
        "closelayer": (GObject.SignalFlags.RUN_FIRST, None, (str,)),
        "submap": (GObject.SignalFlags.RUN_FIRST, None, (str,)),
    }
    """
    Base class for listening to Hyprland events.
    You should not use this class directly
    """
    def __init__(self, event_list: list):
        """
        Initializes an instance of the class.

        Parameters:
            event_list (list): A list of hyprland events.

        Returns:
            None
        """
        self.AVAILABLE_EVENTS = event_list

        self.running = True
        self.loop_thread = threading.Thread(target=self._run)

        self.sock_hypr_events = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        self.sock_hypr_events.settimeout(9)
        self.sock_hypr_events.connect(f'/tmp/hypr/{os.getenv("HYPRLAND_INSTANCE_SIGNATURE")}/.socket2.sock')
        
        self.loop_thread.start()
        
        super().__init__()

    def _run(self, *args):
        while self.running:
            data: str = self.sock_hypr_events.recv(4096).decode().split('>>')
            # event, args = data.split('>>')
            # args = args.split(',')
            
            event = data[0]
            args = data[1].split(',') if len(data) > 1 else []

            if event in self.AVAILABLE_EVENTS:
                self.emit(event, *args)

    def close(self):
        self.sock_hypr_events.close()
#        self.loop_thread.unref()

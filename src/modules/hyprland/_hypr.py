import threading
import logging
import socket
import os

from gi.repository import GObject, GLib

class BaseHyprlandClass:
    def __init__(self):
        """
        Initialize the object.

        This function creates a socket connection to the Unix domain socket at the specified path. The socket uses the AF_UNIX address family and the SOCK_STREAM socket type. The path to the socket file is constructed using the environment variable HYPRLAND_INSTANCE_SIGNATURE.

        Parameters:
            self (object): The object itself.

        Returns:
            None
        """
        self.sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        self.sock.connect(f'/tmp/hypr/{os.getenv("HYPRLAND_INSTANCE_SIGNATURE")}/.socket.sock')

    def send(self, cmd, *args):
        """
        Send a command to the hyprland ipc.

        Args:
            cmd (str): The command to send.
            *args: Additional arguments to include with the command.

        Returns:
            None
        """
        self.sock.send(f'{cmd} {" ".join(args)}'.encode())
        return self.sock.recv(4096).decode()
    
    def close(self):
        """
        Close the socket connection.

        This function closes the socket connection by calling the `close()` method on the `sock` object.

        Parameters:
            None

        Returns:
            None
        """
        self.sock.close()

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
        self.loop_thread.unref()
from modules.hyprland._hypr import BaseHyprlandEventsClass, BaseHyprlandClass
from gi.repository import GObject
import json

class MonitorWorkspace:
    def __init__(self, act_wk_obj: dict):
        self.id: int = act_wk_obj["id"]
        self.name: str = act_wk_obj["name"]

class Monitor(BaseHyprlandClass):
    """
    A class representing a monitor.
    You can access its properties via the attributes of the class.

    """
    
    def __init__(self, mon_obj):
        """
        Initializes a new instance of the Monitor class.
        
        Parameters:
            mon_obj (dict): A dictionary containing the properties of the monitor.
                    
        Returns:
            None
        """
        super().__init__()
        
        self.id: int = mon_obj["id"]
        self.name: str = mon_obj["name"]
        self.description: str = mon_obj["description"]
        self.make: str = mon_obj["make"]
        self.model: str = mon_obj["model"]
        self.serial: str = mon_obj["serial"]
        self.width: int = mon_obj["width"]
        self.height: int = mon_obj["height"]
        self.refreshRate: int = mon_obj["refreshRate"]
        self.x: int = mon_obj["x"]
        self.y: int = mon_obj["y"]
        self.activeWorkspace: MonitorWorkspace = MonitorWorkspace(mon_obj["activeWorkspace"])
        self.specialWorkspace: MonitorWorkspace = MonitorWorkspace(mon_obj["specialWorkspace"])
        self.reserved: list[int] = mon_obj["reserved"]
        self.scale: int = mon_obj["scale"]
        self.transform: int = mon_obj["transform"]
        self.focused: bool = mon_obj["focused"]
        self.dpmsStatus: bool = mon_obj["dpmsStatus"]
        self.vrr: bool = mon_obj["vrr"]
        self.activelyTearing: bool = mon_obj["activelyTearing"]

class Monitors(BaseHyprlandClass, BaseHyprlandEventsClass):
    def __init__(self):
        BaseHyprlandClass.__init__(self)
        BaseHyprlandEventsClass.__init__(self, ["focusedmon", "monitoradded", "monitorremoved"])

        self.monitor_list = []

        self.connect_monitorAdded(self._sync_monitors)
        self.connect_monitorRemoved(self._sync_monitors)

        self._sync_monitors(None)

    def _sync_monitors(self, _):
        self.monitor_list = list(map(lambda x: Monitor(x), json.loads(self.send('j/monitors'))))

    def connect_focusedMon(self, func, args=[]):
        self.connect("focusedmon", func, *args)
    
    def connect_monitorAdded(self, func, args=[]):
        self.connect("monitoradded", func, *args)
    
    def connect_monitorRemoved(self, func, args=[]):
        self.connect("monitorremoved", func, *args)
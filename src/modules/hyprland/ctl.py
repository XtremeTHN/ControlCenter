from modules.hyprland._hypr import HyprctlClass
import json

def deserialize_dict(self, dictionary: dict):
    for key, value in dictionary.items():
        if isinstance(value, dict):
            # deserialize_dict(self,value)
            continue
        if getattr(self, key, "") == "":
            setattr(self, key, value)

class Monitor:
    def __init__(self, **kwargs):
        """
        Monitor class.
        The majority of the properties are merely for information.
        This properties will not be ignored:
            name, resolution, refreshRate, x, y, scale
        """
        self.id: int
        self.name: str
        self.description: str
        self.make: str
        self.model: str
        self.serial: str
        self.width: int
        self.height: int
        self.refreshRate: float
        self.x: int
        self.y: int
        self.reserved: list[int]
        self.scale: float
        self.transform: int
        self.focused: bool

        # Display Power Management Signaling
        self.dpmStatus: bool

        # Variable Refresh Rate
        self.vrr: bool

        # Screen Tearing, idk what this is for
        self.activelyTearing: bool
        
        deserialize_dict(self, kwargs)

class HyprCtl(HyprctlClass):
    def __init__(self):
        super().__init__()

    def setCursor(self, cursor_theme_name: str, cursor_size: int):
        """
        Sets the cursor theme and reloads the cursor manager. Will set the theme for everything except GTK, because GTK.
        """
        return self.exec("setcursor", cursor_theme_name, str(cursor_size))
    
    def getMonitors(self) -> list[Monitor]:
        monitors = json.loads(self.exec("monitors", "-j"))
        mons = []
        for x in monitors:
            mons.append(Monitor(**x))
        
        return mons
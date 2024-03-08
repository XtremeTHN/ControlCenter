from modules.hyprland._hypr import HyprctlClass

class HyprCtl(HyprctlClass):
    def __init__(self):
        super().__init__()

    def setCursor(self, cursor_theme_name: str, cursor_size: int):
        """
        Sets the cursor theme and reloads the cursor manager. Will set the theme for everything except GTK, because GTK.
        """
        return self.exec("setcursor", cursor_theme_name, str(cursor_size))
    
    

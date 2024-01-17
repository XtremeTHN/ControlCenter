from modules.variable import Variable
import os

CONFIG = {
    "Appearance": {
        "CustomTheme": Variable('Catppuccin-Mocha-Standard-Mauve-Dark'),
        "IconTheme": Variable('Adwaita'),
        "CursorTheme": Variable('Bibata-Modern-Classic'),
        "Wallpaper": Variable('')
    },
    "Notifications": {
        "doNotDisturb": Variable(False),
        'duration': Variable(5),
        "notificationAppearance": {
            'blur': Variable(False),
            'opacity': Variable(0.5),
        }
    },
    "User": {
        "name": os.getenv('USER'),
        "userPhoto": Variable('avatar-default'),
        
    }
}
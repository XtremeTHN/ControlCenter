from modules.variable import Variable
import os
import json

CONFIG = {
    "Appearance": {
        "CustomTheme": 'Catppuccin-Mocha-Standard-Mauve-Dark',
        "IconTheme": 'Adwaita',
        "CursorTheme": 'Bibata-Modern-Classic',
        "Wallpaper": ''
    },
    "Notifications": {
        "doNotDisturb": False,
        'duration': 5,
        "notificationAppearance": {
            'blur': False,
            'opacity': 0.5,
        }
    },
    "User": {
        "userName": os.getenv('USER'),
        "userPhoto": 'avatar-default',
    },
    "LoginManager": {
        "theme": '',
        "autoLogin": {
            "user": "",
            "password": "",
            "session": ""
        }
    },
    "Plymouth": {
        'emabled': True,
        'theme': '',
        
    }
}

def dump_config():
    with open(f'{os.getenv("HOME")}/.config/ags/centerConfig.json', 'w') as file:
        json.dump(CONFIG, file, indent=4)
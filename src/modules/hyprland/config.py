import logging

class HyprConfig:
    def __init__(self):
        self.logger = logging.getLogger('HyprConfig')
        self.logger.warning("This class only works if the Hyprland configuration is divided into different files")
        self.logger.warning("If you are using my dotfiles, this shouldn't be an issue")

        ...
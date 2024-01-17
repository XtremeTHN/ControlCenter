from gi.repository import GObject

class Variable(GObject.GObject):
    def __init__(self, value):
        super().__init__()

        self.value = GObject.Property(type=type(value), default=value)
    
    def __str__(self):
        return str(self.value)
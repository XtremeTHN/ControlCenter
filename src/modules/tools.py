from gi.repository import Gtk, Gio

def set_margins(widget: Gtk.Widget, margins: list[int]):
    length = len(margins)
    
    top = margins[0]
    right = margins[1] if length > 1 else top
    bottom = margins[2] if length > 2 else right
    left = margins[3] if length > 3 else bottom

    widget.set_margin_top(top)
    widget.set_margin_end(right)
    widget.set_margin_bottom(bottom)
    widget.set_margin_start(left)

def include_file(file: str) -> str:
    gfile = Gio.File.new_for_path(file)

    return gfile.load_contents(None)[1].decode('utf-8')

def include_bytes(file: str) -> bytes:
    gfile = Gio.File.new_for_path(file)
    return gfile.load_contents(None)[1]

def HBox(spacing=10, **extra) -> Gtk.Box:
    return Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=spacing, **extra)

def VBox(spacing=10, **extra) -> Gtk.Box:
    return Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=spacing, **extra)

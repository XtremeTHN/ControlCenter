from gi.repository import Adw, Gtk, Gio

from pathlib import Path

def set_margins(widget: Gtk.Widget, margins: list[int]):
    """
        Reminder: margins = [top, right, bottom, left]
    """
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
    """
    Opens a file, reads it, and return it's contents.
    It uses Gio.File for reading the file.

    Args:
        file (str): The file path

    Returns:
        str: The contents of the file
    """
    gfile = Gio.File.new_for_path(file)
    if gfile.query_exists() is not False:
        return gfile.load_contents(None)[1].decode('utf-8')
    else:
        return ""

def include_bytes(file: str) -> bytes:
    """
    Same to include_file but instead of a string returns bytes

    Args:
        file (str): The file path

    Returns:
        bytes: The contents of the file in bytes
    """
    gfile = Gio.File.new_for_path(file)
    return gfile.load_contents(None)[1]
    
def create_empty_file(file: str):
    """
    Creates an empty file

    Args:
        file (str): The file path
    """
    open(file, 'x').close()


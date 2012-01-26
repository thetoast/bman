from ctypes import windll, byref, Structure
from ctypes.wintypes import SHORT, WORD, DWORD
from win32console import *

from console import Console
from errors import BManError


class COORD(Structure):
  """struct in wincon.h."""
  _fields_ = [
    ("X", SHORT),
    ("Y", SHORT)]


class SMALL_RECT(Structure):
  """struct in wincon.h."""
  _fields_ = [
    ("Left", SHORT),
    ("Top", SHORT),
    ("Right", SHORT),
    ("Bottom", SHORT)]


class CONSOLE_SCREEN_BUFFER_INFO(Structure):
  """struct in wincon.h."""
  _fields_ = [
    ("dwSize", COORD),
    ("dwCursorPosition", COORD),
    ("wAttributes", WORD),
    ("srWindow", SMALL_RECT),
    ("dwMaximumWindowSize", COORD)]


k32 = windll.kernel32

FOREGROUND_BLACK     = 0x0000
FOREGROUND_BLUE      = 0x0001
FOREGROUND_GREEN     = 0x0002
FOREGROUND_CYAN      = 0x0003
FOREGROUND_RED       = 0x0004
FOREGROUND_MAGENTA   = 0x0005
FOREGROUND_YELLOW    = 0x0006
FOREGROUND_GREY      = 0x0007
FOREGROUND_INTENSITY = 0x0008 # foreground color is intensified.


color_map = {
    "black" : 0,
    "blue" : FOREGROUND_BLUE | FOREGROUND_INTENSITY,
    "green" : FOREGROUND_GREEN | FOREGROUND_INTENSITY,
    "cyan" : FOREGROUND_BLUE | FOREGROUND_GREEN | FOREGROUND_INTENSITY,
    "red" : FOREGROUND_RED | FOREGROUND_INTENSITY,
    "magenta" : FOREGROUND_RED | FOREGROUND_BLUE | FOREGROUND_INTENSITY,
    "yellow" : FOREGROUND_RED | FOREGROUND_GREEN | FOREGROUND_INTENSITY,
    "grey" : FOREGROUND_RED | FOREGROUND_BLUE | FOREGROUND_GREEN,
    "white" : FOREGROUND_RED | FOREGROUND_BLUE | FOREGROUND_GREEN | FOREGROUND_INTENSITY,
}


class Win32ConsoleError(BManError): pass


class Win32Console(Console):
    def __init__(self, *args, **kwargs):
        Console.__init__(self, *args, **kwargs)
        self.stdout = k32.GetStdHandle(STD_OUTPUT_HANDLE)

    def set_color(self, color=None):

        if color is not None:
            norm = color.lower()
            try:
                real_color = color_map[norm]
            except KeyError, e:
                raise Win32ConsoleError("Invalid color: %s" % (color))

            self._set_color(real_color)

    def _set_color(self, color):
        k32.SetConsoleTextAttribute(self.stdout, color)

    def restore_color(self):
        self._set_color(self.saved_color)

    def save_color(self):
        csbi = CONSOLE_SCREEN_BUFFER_INFO()
        k32.GetConsoleScreenBufferInfo(self.stdout, byref(csbi))
        self.saved_color = csbi.wAttributes

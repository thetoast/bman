from sys import platform

if platform.startswith('win32'):
    from win32 import Win32Console as Console
else:
    from console import Console as Console

import gi
import subprocess
import src.mainwindow

gi.require_version('Gtk', '3.0')
from gi.repository import Gtk

def quit_all(arg):
    # idk what arg is supposed to be, but it needs one argument
    subprocess.call(['pactl', 'unload-module', 'module-null-sink'])
    subprocess.call(['pkill', 'sox'])

    Gtk.main_quit()

if __name__ == '__main__':
    win = src.mainwindow.MainWindow()
    win.connect('destroy', quit_all)
    win.show_all()

    Gtk.main()

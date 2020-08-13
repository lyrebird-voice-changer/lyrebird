#!/usr/bin/env python3
import gi
import subprocess

import src.mainwindow as mainwindow
import src.core.utils as utils

gi.require_version('Gtk', '3.0')
from gi.repository import Gtk

def quit_all(arg):
    # idk what arg is supposed to be, but it needs one argument
    utils.kill_sink(check_state=False)

    Gtk.main_quit()

if __name__ == '__main__':
    win = mainwindow.MainWindow()
    win.connect('destroy', quit_all)
    win.show_all()

    Gtk.main()

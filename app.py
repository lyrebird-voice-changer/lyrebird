#!/usr/bin/env python3
import gi
import subprocess

import lyrebird.mainwindow as mainwindow
import lyrebird.core.utils as utils

gi.require_version('Gtk', '3.0')
from gi.repository import Gtk


if __name__ == '__main__':
    win = mainwindow.MainWindow()
    win.connect('destroy', win.close)
    win.show_all()

    try:
        Gtk.main()
    except BaseException as e:
        win.close()
        raise e

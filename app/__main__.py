#!/usr/bin/env python3
import gi
import app.mainwindow as mainwindow

gi.require_version('Gtk', '3.0')
from gi.repository import Gtk


def main():
    win = mainwindow.MainWindow()
    win.connect('destroy', win.close)
    win.show_all()

    try:
        Gtk.main()
    except BaseException as e:
        win.close()
        raise e


if __name__ == '__main__':
    main()

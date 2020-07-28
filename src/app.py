import gi
import mainwindow

gi.require_version('Gtk', '3.0')
from gi.repository import Gtk

if __name__ == '__main__':
    win = mainwindow.MainWindow()
    win.show_all()

    Gtk.main()
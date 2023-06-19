#!/usr/bin/env python3
import gi
import sys

import app.mainwindow as mainwindow
import app.core.utils as utils

gi.require_version('Gtk', '4.0')
from gi.repository import Gio, Gtk

class Lyrebird(Gtk.Application):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.connect('activate', self.on_activate)

    def on_activate(self, app):
        self.win = mainwindow.MainWindow(application=app)
        self.win.present()

app = Lyrebird(application_id="org.lyrebird.Lyrebird")
app.run(sys.argv)

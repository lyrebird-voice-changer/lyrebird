import gi
from gi.repository import Gtk, Gdk, GdkPixbuf

class Alert:
    def __init__(self, parent):
        self.parent = parent

    def show_error(self, title, msg):
        '''
        Create an error message dialog with title and markup message.
        '''
        dialog = Gtk.MessageDialog(
            parent         = self.parent,
            type           = Gtk.MessageType.ERROR,
            buttons        = Gtk.ButtonsType.OK)
        if self.parent:
            dialog.set_transient_for(self.parent)
        dialog.set_title(title)
        dialog.set_markup(msg)

        dialog.show()
        dialog.run()
        dialog.destroy()

#!/bin/python

import gi
import subprocess

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, Gdk, GdkPixbuf

# Multiplier for pitch shifting
sox_multiplier = 100

pitch_effects = [
    ("Man",         "1.5"),
    ("Woman",       "2.5"),
    ("Boy",         "1.25"),
    ("Girl",        "3.5"),
    ("Darth\nVader","-6.0"),
    ("Satan",       "-10.0"),
    ("Helium",      "5.0"),
    ("Chipmunk",    "10.0")
]

class MainWindow(Gtk.Window):
    """
    Main window for Lyrebird
    Lyrebird is a simple and powerful voice changer for Linux, written in GTK 3.
    """

    def __init__(self):
        Gtk.Window.__init__(self, title="Lyrebird")
        self.set_border_width(10)

        self.set_size_request(600, 500)
        self.set_default_size(600, 500)

        headerbar = Gtk.HeaderBar()
        headerbar.set_show_close_button(True)
        headerbar.props.title = "Lyrebird"

        about_btn = Gtk.Button()
        about_btn.props.image = Gtk.Button.new_from_icon_name("help-about-symbolic", Gtk.IconSize.BUTTON)
        about_btn.connect("clicked", self.about_clicked)
        headerbar.pack_start(about_btn)

        open_pavucontrol_btn = Gtk.Button()
        open_pavucontrol_btn.props.image = Gtk.Button.new_from_icon_name("audio-x-generic-symbolic", Gtk.IconSize.BUTTON)
        open_pavucontrol_btn.connect("clicked", self.open_pavucontrol_clicked)
        headerbar.pack_start(open_pavucontrol_btn)

        self.set_titlebar(headerbar)

        # Unload the null sink module if there is one from last time.
        # The only reason there would be one already, if if the application was closed without
        # toggling the switch to off.
        subprocess.call(["pactl", "unload-module", "module-null-sink"])

        # Build the UI
        self.build_ui()

    def build_ui(self):
        self.vbox = Gtk.VBox()

        # Toggle switch for Lyrebird
        self.hbox_toggle = Gtk.HBox()
        self.toggle_label = Gtk.Label("Toggle Lyrebird")
        self.toggle_label.set_halign(Gtk.Align.START)

        self.toggle_switch = Gtk.Switch()
        self.toggle_switch.set_size_request(10, 25)
        self.toggle_switch.connect("notify::active", self.toggle_activated)
        self.hbox_toggle.pack_start(self.toggle_label, False, False, 0)
        self.hbox_toggle.pack_end(self.toggle_switch, False, False, 0)

        # Pitch shift scale
        self.hbox_pitchshift = Gtk.HBox()
        self.pitchshift_label = Gtk.Label("Pitch Shift ")
        self.pitchshift_label.set_halign(Gtk.Align.START)   

        self.pitch_adj = Gtk.Adjustment(0, -10, 10, 5, 10, 0)
        self.pitchshift_scale = Gtk.Scale(orientation=Gtk.Orientation.HORIZONTAL, adjustment=self.pitch_adj)
        self.pitchshift_scale.set_valign(Gtk.Align.CENTER)
        self.pitchshift_scale.connect("value-changed", self.pitchshift_scale_moved)
        
        self.hbox_pitchshift.pack_start(self.pitchshift_label, False, False, 0)
        self.hbox_pitchshift.pack_end(self.pitchshift_scale, True, True, 0)

        # Flowbox containing the effects
        self.effects_label = Gtk.Label()
        self.effects_label.set_markup("<b>Effects</b>")
        self.effects_label.set_halign(Gtk.Align.START)   

        self.flowbox = Gtk.FlowBox()
        self.flowbox.set_valign(Gtk.Align.START)
        self.flowbox.set_max_children_per_line(5)
        self.flowbox.set_selection_mode(Gtk.SelectionMode.NONE)

        # Create the flow box items
        self.create_flowbox_items(self.flowbox)

        self.vbox.pack_start(self.hbox_toggle, False, False, 5)
        self.vbox.pack_start(self.hbox_pitchshift, False, False, 5)
        self.vbox.pack_start(self.effects_label, False, False, 5)
        self.vbox.pack_end(self.flowbox, True, True, 0)

        self.add(self.vbox)

    def create_flowbox_items(self, flowbox):
        global pitch_effects
        for (name, pitch) in pitch_effects:
            button = Gtk.Button()
            button.set_size_request(80, 80)

            button.set_label(name)
            button.connect("clicked", self.pitch_effect_clicked)
            flowbox.add(button)

    # Event handlers
    def about_clicked(self, button):
        about = Gtk.AboutDialog()
        about.set_program_name("Lyrebird")
        about.set_copyright("(c) charlotte 2020")
        about.set_comments("Simple and powerful voice changer for Linux, written in GTK 3")
        about.set_logo(GdkPixbuf.Pixbuf.new_from_file("icon.png"))

        about.run()
        about.destroy()

    def open_pavucontrol_clicked(self, button):
        subprocess.call(["pavucontrol"])

    def toggle_activated(self, switch, gparam):
        if switch.get_active():
            # Load module-null-sink
            subprocess.call(["pactl", "load-module", "module-null-sink"])

            # Kill the sox process
            subprocess.call(["pkill", "sox"])

            # Multiply the pitch shift scale value by the multiplier and feed it to sox
            pitch_shift = self.pitchshift_scale.get_value() * sox_multiplier
            sox_process = subprocess.Popen(["sox", "--buffer", "1024", "-q", "-t", "pulseaudio", "default", "-t", "pulseaudio", "null", "pitch", str(pitch_shift)])
        else:
            dialog = Gtk.MessageDialog(
                transient_for=self,
                message_type=Gtk.MessageType.INFO,
                buttons=Gtk.ButtonsType.OK,
                text="Unloaded module-null-sink"
            )

            dialog.format_secondary_text("PulseAudio Null Output sink has been unloaded. Lyrebird will no longer work.")

            dialog.run()
            dialog.destroy()

            # Unload module-null-sink
            subprocess.call(["pactl", "unload-module", "module-null-sink"])

            # Kill the sox process
            subprocess.call(["pkill", "sox"])

    def pitchshift_scale_moved(self, event):
        global sox_multiplier
        # FIXME: Very hacky code, we repeatedly kill sox, grab the new value to pitch shift
        # by, and then restart the process. Not sure if theres a better way to do this but there
        # has to be lol.

        # Kill the sox process
        subprocess.call(["pkill", "sox"])

        # Multiply the pitch shift scale value by the multiplier and feed it to sox
        pitch_shift = self.pitchshift_scale.get_value() * sox_multiplier
        sox_process = subprocess.Popen(["sox", "--buffer", "1024", "-q", "-t", "pulseaudio", "default", "-t", "pulseaudio", "null", "pitch", str(pitch_shift)])

    def pitch_effect_clicked(self, button):
        global pitch_effects, sox_multiplier
        effect = None

        # TODO: Replace this so its more efficient
        for (name, pitch) in pitch_effects:
            if name == button.props.label:
                effect = (name, pitch)
                break

        self.pitchshift_scale.set_value(float(effect[1]))
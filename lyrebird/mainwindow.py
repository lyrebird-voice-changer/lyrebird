#!/bin/python

import gi
import subprocess

gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, Gdk, GdkPixbuf

# Core imports
import lyrebird.core.presets as presets
import lyrebird.core.state as state
import lyrebird.core.config as config
import lyrebird.core.utils as utils

from lyrebird.core.presets import Preset

# Multiplier for pitch shifting
sox_multiplier = 100

class MainWindow(Gtk.Window):
    '''
    Main window for Lyrebird
    Lyrebird is a simple and powerful voice changer for Linux, written in GTK 3.
    '''

    def __init__(self):
        Gtk.Window.__init__(self, title='Lyrebird')
        self.set_border_width(10)

        self.set_size_request(600, 500)
        self.set_default_size(600, 500)

        headerbar = Gtk.HeaderBar()
        headerbar.set_show_close_button(True)
        headerbar.props.title = 'Lyrebird Voice Changer'

        about_btn = Gtk.Button.new_from_icon_name('help-about-symbolic', Gtk.IconSize.BUTTON);
        about_btn.connect('clicked', self.about_clicked)
        headerbar.pack_start(about_btn)

        self.set_wmclass ('Lyrebird', 'Lyrebird')
        self.set_title('Lyrebird')
        self.set_titlebar(headerbar)

        self.sox_process = None

        # Unload the null sink module if there is one from last time.
        # The only reason there would be one already, is if the application was closed without
        # toggling the switch to off (aka a crash was experienced).
        utils.unload_pa_modules(check_state=False)

        # Load the configuration file
        state.config = config.load_config()

        # Set the icon
        self.set_icon_from_file('icon.png')

        # Build the UI
        self.build_ui()


    def build_ui(self):
        self.vbox = Gtk.VBox()

        # Toggle switch for Lyrebird
        self.hbox_toggle = Gtk.HBox()
        self.toggle_label = Gtk.Label('Toggle Lyrebird')
        self.toggle_label.set_halign(Gtk.Align.START)

        self.toggle_switch = Gtk.Switch()
        self.toggle_switch.set_size_request(10, 25)
        self.toggle_switch.connect('notify::active', self.toggle_activated)
        self.hbox_toggle.pack_start(self.toggle_label, False, False, 0)
        self.hbox_toggle.pack_end(self.toggle_switch, False, False, 0)

        # Pitch shift scale
        self.hbox_pitch = Gtk.HBox()
        self.pitch_label = Gtk.Label('Pitch Shift ')
        self.pitch_label.set_halign(Gtk.Align.START)

        self.pitch_adj = Gtk.Adjustment(0, -10, 10, 5, 10, 0)
        self.pitch_scale = Gtk.Scale(orientation=Gtk.Orientation.HORIZONTAL, adjustment=self.pitch_adj)
        self.pitch_scale.set_valign(Gtk.Align.CENTER)
        self.pitch_scale.connect('value-changed', self.pitch_scale_moved)

        # By default, disable the pitch shift slider to force the user to pick an effect
        self.pitch_scale.set_sensitive(False)

        self.hbox_pitch.pack_start(self.pitch_label, False, False, 0)
        self.hbox_pitch.pack_end(self.pitch_scale, True, True, 0)

        # Flow box containing the presets
        self.effects_label = Gtk.Label()
        self.effects_label.set_markup('<b>Presets</b>')
        self.effects_label.set_halign(Gtk.Align.START)

        self.flowbox = Gtk.FlowBox()
        self.flowbox.set_valign(Gtk.Align.START)
        self.flowbox.set_max_children_per_line(5)
        self.flowbox.set_selection_mode(Gtk.SelectionMode.NONE)

        # Create the flow box items
        self.create_flowbox_items(self.flowbox)

        self.vbox.pack_start(self.hbox_toggle, False, False, 5)
        self.vbox.pack_start(self.hbox_pitch, False, False, 5)
        self.vbox.pack_start(self.effects_label, False, False, 5)
        self.vbox.pack_end(self.flowbox, True, True, 0)

        self.add(self.vbox)

    def create_flowbox_items(self, flowbox):
        state.loaded_presets = presets.load_presets()

        for preset in state.loaded_presets:
            button = Gtk.Button()
            button.set_size_request(80, 80)

            button.set_label(preset.name)
            button.connect('clicked', self.preset_clicked)
            flowbox.add(button)

    # Event handlers
    def about_clicked(self, button):
        about = Gtk.AboutDialog()
        about.set_program_name('Lyrebird Voice Changer')
        about.set_version("v1.0.1")
        about.set_copyright('(c) Charlotte 2020')
        about.set_comments('Simple and powerful voice changer for Linux, written in GTK 3')
        about.set_logo(GdkPixbuf.Pixbuf.new_from_file('icon.png'))

        about.run()
        about.destroy()

    def toggle_activated(self, switch, gparam):
        if switch.get_active():
            # Load module-null-sink
            null_sink = subprocess.check_call(
                'pacmd load-module module-null-sink sink_name=Lyrebird-Output'.split(' ')
            )
            remap_sink = subprocess.check_call(
                'pacmd load-module module-remap-source source_name=Lyrebird-Input master=Lyrebird-Output.monitor'\
                    .split(' ')
            )

            print(f'Loaded null output sink ({null_sink}), and remap sink ({remap_sink})')

            subprocess.check_call(
                'pacmd update-sink-proplist Lyrebird-Output device.description="Lyrebird Output"'\
                    .split(' ')
            )
            subprocess.check_call(
                'pacmd update-source-proplist Lyrebird-Input device.description="Lyrebird Virtual Input"'\
                    .split(' ')
            )


            state.sink = null_sink

            # Kill the sox process
            self.terminate_sox()

            # Use the default preset, which is "Man" if the loaded preset is not found.
            default_preset = state.loaded_presets[0]

            current_preset = state.current_preset or default_preset
            if current_preset.override_pitch:
                # Set the pitch of the slider
                self.pitch_scale.set_value(float(current_preset.pitch_value))
                self.pitch_scale.set_sensitive(False)

                command = utils.build_sox_command(
                    current_preset,
                    config_object=state.config
                )
            else:
                self.pitch_scale.set_sensitive(True)
                command = utils.build_sox_command(
                    current_preset,
                    config_object=state.config,
                    scale_object=self.pitch_scale
                )
            self.sox_process = subprocess.Popen(command.split(' '))
        else:
            utils.unload_pa_modules(check_state=True)
            self.terminate_sox()

    def pitch_scale_moved(self, event):
        global sox_multiplier
        # Very hacky code, we repeatedly kill sox, grab the new value to pitch shift
        # by, and then restart the process.

        # Only allow adjusting the pitch if the preset doesn't override the pitch
        if state.current_preset is not None:
            # Kill the sox process
            self.terminate_sox()

            if not state.current_preset.override_pitch:
                # Multiply the pitch shift scale value by the multiplier and feed it to sox
                command = utils.build_sox_command(
                    state.current_preset,
                    config_object=state.config,
                    scale_object=self.pitch_scale
                )
                self.sox_process = subprocess.Popen(command.split(' '))

    def preset_clicked(self, button):
        global sox_multiplier
        self.terminate_sox()

        # Use a filter to find the currently selected preset
        current_preset = list(filter(lambda p: p.name == button.props.label, state.loaded_presets))[0]
        state.current_preset = current_preset

        if current_preset.override_pitch:
            # Set the pitch of the slider
            self.pitch_scale.set_value(float(current_preset.pitch_value))
            self.pitch_scale.set_sensitive(False)

            command = utils.build_sox_command(
                state.current_preset,
                config_object=state.config
            )
        else:
            self.pitch_scale.set_sensitive(True)
            command = utils.build_sox_command(
                state.current_preset,
                config_object=state.config,
                scale_object=self.pitch_scale
            )

        self.sox_process = subprocess.Popen(command.split(' '))

    def terminate_sox(self, timeout=1):
        if self.sox_process is not None:
            self.sox_process.terminate()
            try:
                self.sox_process.wait(timeout=timeout)
            except subprocess.TimeoutExpired:
                self.sox_process.kill()
                self.sox_process.wait(timeout=timeout)
            self.sox_process = None

    def close(self, *args):
        self.terminate_sox()
        utils.unload_pa_modules(check_state=False)
        Gtk.main_quit()

#!/bin/python

import gi
import subprocess

gi.require_version('Gtk', '4.0')
from gi.repository import Gtk, Gdk, GdkPixbuf

# Core imports
import app.core.presets as presets
import app.core.state as state
import app.core.config as config
import app.core.utils as utils

from app.core.presets import Preset

# Multiplier for pitch shifting
sox_multiplier = 100

class MainWindow(Gtk.ApplicationWindow):
    '''
    Main window for Lyrebird
    Lyrebird is a simple and powerful voice changer for Linux, written in GTK.
    '''

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.set_size_request(600, 500)
        self.set_default_size(600, 500)

        headerbar = Gtk.HeaderBar()
        headerbar.set_show_title_buttons(True)

        about_btn = Gtk.Button.new_from_icon_name('help-about-symbolic');
        about_btn.connect('clicked', self.about_clicked)
        headerbar.pack_start(about_btn)

        self.set_title('Lyrebird')
        self.set_titlebar(headerbar)

        # Create the lock file to ensure only one instance of Lyrebird is running at once
        lock_file = utils.place_lock()
        if lock_file is None:
            self.show_error_message("Lyrebird Already Running", "Only one instance of Lyrebird can be ran at a time.")
            exit(1)
        else:
            self.lock_file = lock_file

        # Setup for handling SoX process
        self.sox_process = None

        # Unload the null sink module if there is one from last time.
        # The only reason there would be one already, is if the application was closed without
        # toggling the switch to off (aka a crash was experienced).
        utils.unload_pa_modules()

        # Load the configuration file
        state.config = config.load_config()

        # Build the UI
        self.build_ui()

    def show_error_message(self, title, msg):
        '''
        Create an error message dialog with title and string message.
        '''
        dialog = Gtk.MessageDialog(
            parent         = self,
            type           = Gtk.MessageType.ERROR,
            buttons        = Gtk.ButtonsType.OK,
            message_format = msg)
        dialog.set_transient_for(self)
        dialog.set_title(title)

        dialog.show()
        dialog.run()
        dialog.destroy()

    def build_ui(self):
        self.vbox = Gtk.Box.new(Gtk.Orientation.VERTICAL, 5)
        self.vbox.set_margin_start(10)
        self.vbox.set_margin_end(10)
        self.vbox.set_margin_top(10)
        self.vbox.set_margin_bottom(10)

        # Toggle switch for Lyrebird
        self.hbox_toggle = Gtk.Box.new(Gtk.Orientation.HORIZONTAL, 0)
        self.toggle_label = Gtk.Label.new('Toggle Lyrebird')
        self.toggle_label.set_halign(Gtk.Align.START)
        self.toggle_label.set_hexpand(True)

        self.toggle_switch = Gtk.Switch()
        self.toggle_switch.set_size_request(10, 25)
        self.toggle_switch.connect('notify::active', self.toggle_activated)
        self.hbox_toggle.append(self.toggle_label)
        self.hbox_toggle.append(self.toggle_switch)

        # Pitch shift scale
        self.hbox_pitch = Gtk.Box.new(Gtk.Orientation.HORIZONTAL, 0)
        self.pitch_label = Gtk.Label.new('Pitch Shift ')
        self.pitch_label.set_halign(Gtk.Align.START)

        self.pitch_adj = Gtk.Adjustment.new(0, -10, 10, 5, 10, 0)
        self.pitch_scale = Gtk.Scale(orientation=Gtk.Orientation.HORIZONTAL, adjustment=self.pitch_adj)
        self.pitch_scale.set_valign(Gtk.Align.CENTER)
        self.pitch_scale.set_hexpand(True)
        self.pitch_scale.connect('value-changed', self.pitch_scale_moved)

        # By default, disable the pitch shift slider to force the user to pick an effect
        self.pitch_scale.set_sensitive(False)

        self.hbox_pitch.append(self.pitch_label)
        self.hbox_pitch.append(self.pitch_scale)

        # Flow box containing the presets
        self.effects_label = Gtk.Label()
        self.effects_label.set_markup('<b>Presets</b>')
        self.effects_label.set_halign(Gtk.Align.START)

        self.flowbox = Gtk.FlowBox()
        self.flowbox.set_valign(Gtk.Align.START)
        self.flowbox.set_hexpand(True)
        self.flowbox.set_max_children_per_line(5)
        self.flowbox.set_selection_mode(Gtk.SelectionMode.NONE)

        # Create the flow box items
        self.create_flowbox_items(self.flowbox)

        self.vbox.append(self.hbox_toggle)
        self.vbox.append(self.hbox_pitch)
        self.vbox.append(self.effects_label)
        self.vbox.append(self.flowbox)

        self.set_child(self.vbox)

    def create_flowbox_items(self, flowbox):
        state.loaded_presets = presets.load_presets()

        for preset in state.loaded_presets:
            button = Gtk.Button()
            button.set_size_request(80, 80)

            button.set_label(preset.name)
            button.connect('clicked', self.preset_clicked)
            flowbox.append(button)

    # Event handlers
    def about_clicked(self, button):
        about = Gtk.AboutDialog()
        about.set_program_name('Lyrebird Voice Changer')
        about.set_version("v1.1.0")
        about.set_copyright('(c) Lyrebird 2020-2022')
        about.set_comments('Simple and powerful voice changer for Linux, written in GTK')
        about.set_logo(GdkPixbuf.Pixbuf.new_from_file('icon.png'))

        about.run()
        about.destroy()

    def toggle_activated(self, switch, gparam):
        if switch.get_active():
            # Load module-null-sink
            null_sink = subprocess.check_call(
                'pactl load-module module-null-sink sink_name=Lyrebird-Output node.description="Lyrebird Output"'.split(' ')
            )
            remap_sink = subprocess.check_call(
                'pactl load-module module-remap-source source_name=Lyrebird-Input master=Lyrebird-Output.monitor node.description="Lyrebird Virtual Input"'\
                    .split(' ')
            )

            print(f'Loaded null output sink and remap sink')

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
            utils.unload_pa_modules()
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
        self.lock_file.close()
        utils.destroy_lock()
        utils.unload_pa_modules()
        Gtk.main_quit()

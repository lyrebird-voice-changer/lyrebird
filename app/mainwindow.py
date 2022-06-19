#!/bin/python

import gi
import subprocess

gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, Gdk, GdkPixbuf

# Core imports
import app.core.presets as presets
import app.core.state as state
import app.core.config as config
import app.core.utils as utils

from app.core.presets import Preset

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
        headerbar.props.title = 'Lyrebird'

        about_btn = Gtk.Button.new_from_icon_name('help-about-symbolic', Gtk.IconSize.BUTTON);
        about_btn.connect('clicked', self.about_clicked)
        headerbar.pack_start(about_btn)

        self.set_wmclass ('Lyrebird', 'Lyrebird')
        self.set_title('Lyrebird')
        self.set_titlebar(headerbar)

        # Set the icon
        self.set_icon_from_file('icon.png')

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
        utils.unload_pa_modules(check_state=False)

        # Load the configuration file
        state.config = config.load_config()

        # To allow switching presets and values before toggling Lyrebird on
        self.activated = False

        # To track all the scales and switches and get the values when needed
        self.effects_scales = {}
        self.effects_switches = {}

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

    def build_parameter_row(self, parameter, effect_name, value_min, value_max, step=None, page_step=None):
        hbox = Gtk.HBox()
        label = Gtk.Label(parameter)
        label.set_halign(Gtk.Align.START)
        label.set_size_request(100, 25)

        switch = Gtk.Switch()
        #switch.set_size_request(40, 25)
        switch.connect('notify::active', self.scale_moved)

        # I'm not sure what step and page step does, so I just used the approach that was used
        # for pitch scale as default
        if step is None:
            step = (value_max - value_min) // 4
        if page_step is None:
            page_step = step * 2

        adj = Gtk.Adjustment(0, value_min, value_max, step, page_step, 0)
        scale = Gtk.Scale(orientation=Gtk.Orientation.HORIZONTAL, adjustment=adj)
        scale.set_valign(Gtk.Align.CENTER)
        scale.connect('value-changed', self.scale_moved)

        # By default, disable the pitch shift slider to force the user to pick an effect
        scale.set_sensitive(False)

        hbox.pack_start(label, False, False, 0)
        hbox.pack_start(switch, False, False, 20)

        hbox.pack_end(scale, True, True, 0)

        self.effects_scales[effect_name] = scale
        self.effects_switches[effect_name] = switch

        self.vbox.pack_start(hbox, False, False, 5)

        return hbox

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

        self.vbox.pack_start(self.hbox_toggle, False, False, 5)

        # Pitch shift scale
        self.build_parameter_row('Pitch Shift ', 'pitch', -1000, 1000)
        # Highpass scale
        self.build_parameter_row('Highpass ', 'highpass', 100, 1000)
        # Lowpass scale
        self.build_parameter_row('Lowpass ', 'lowpass', 200, 4000)

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

    def restart_sox(self):
        # No need to start the process if Lyrebird is toggled off
        if not self.activated:
            return

        self.terminate_sox()

        # Gather values from the scales to one dict
        # take only the values of scales where switch is toggled on
        ui_values = {}

        for effect_name, scale in self.effects_scales.items():
            if self.effects_switches[effect_name].get_active():
                ui_values[effect_name] = scale.get_value()

        command = utils.build_sox_command(
            state.current_preset,
            config_object=state.config,
            ui_values=ui_values
        )

        self.sox_process = subprocess.Popen(command.split(' '))

    def set_preset(self, preset):
        state.current_preset = preset

        for effect_name, scale in self.effects_scales.items():
            # If effect is already in preset, use the value and disable the scale
            if effect_name in preset.effects:
                scale.set_value(preset.effects[effect_name][0])
                scale.set_sensitive(False)
            else:
                scale.set_sensitive(True)

        self.restart_sox()

    # Event handlers
    def about_clicked(self, button):
        about = Gtk.AboutDialog()
        about.set_program_name('Lyrebird Voice Changer')
        about.set_version("v1.1.0")
        about.set_copyright('(c) Charlotte 2020')
        about.set_comments('Simple and powerful voice changer for Linux, written in GTK 3')
        about.set_logo(GdkPixbuf.Pixbuf.new_from_file('icon.png'))

        about.run()
        about.destroy()

    def toggle_activated(self, switch, gparam):
        if switch.get_active():
            self.activated = True
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

            # Use the default preset, which is "Man" if the loaded preset is not found.
            default_preset = state.loaded_presets[0]

            preset = state.current_preset or default_preset
            self.set_preset(preset)
        else:
            self.activated = False
            utils.unload_pa_modules(check_state=True)
            self.terminate_sox()

    def scale_moved(self, event, gparam=None):
        global sox_multiplier
        # Very hacky code, we repeatedly kill sox, grab the new value to pitch shift
        # by, and then restart the process.

        # Only allow adjusting the pitch if the preset doesn't override the pitch
        if state.current_preset is not None:
            self.restart_sox()

    def preset_clicked(self, button):
        global sox_multiplier

        # Use a filter to find the currently selected preset
        preset = list(filter(lambda p: p.name == button.props.label, state.loaded_presets))[0]
        self.set_preset(preset)

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
        utils.unload_pa_modules(check_state=False)
        Gtk.main_quit()

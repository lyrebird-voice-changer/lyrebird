#!/bin/python

import gi
import subprocess

from gi.repository import Gtk, Gdk, GdkPixbuf

# Core imports
import app.core.presets as presets
import app.core.state as state
import app.core.config as config
import app.core.lock as lock
from app.core.presets import Preset
from app.core.audio import Audio

from app.ui.alert import Alert

class MainWindow(Gtk.Window):
    '''
    Main window for Lyrebird
    '''

    def __init__(self):
        Gtk.Window.__init__(self, title='Lyrebird')
        self.set_border_width(10)

        self.set_size_request(600, 500)
        self.set_default_size(600, 500)

        self.alert = Alert(self)

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
        lock_file = lock.place_lock()
        if lock_file is None:
            alert.show_error_markup("Lyrebird Already Running", "Only one instance of Lyrebird can be ran at a time.")
            exit(1)
        else:
            self.lock_file = lock_file

        # Load the configuration file
        try:
            state.config = config.load_config()
        except BaseException as e:
            print(f"[error] Failed to load config file: {str(e)}")
            self.alert.show_warning("Failed to Config File", f"Lyrebird failed to load config, your config.toml file is most likely malformed. See the console for further details.\n\nConfig file location: {config.config_path}")
            # load with default options
            state.config = config.Configuration()

        state.audio = Audio()

        # Unload the null sink module if there is one from last time.
        # The only reason there would be one already, is if the application was closed without
        # toggling the switch to off (aka a crash was experienced).
        state.audio.unload_pa_modules()

        state.loaded_presets = presets.DEFAULT_PRESETS

        try:
            load_presets_state = presets.load_presets()
        
            loaded_presets = load_presets_state["presets"]
            failed_presets = load_presets_state["failed"]

            state.loaded_presets += loaded_presets
            if len(failed_presets) > 0:
                msg = f"The following presets failed to import: {', '.join(failed_presets)}. See the console for more details."
                self.alert.show_warning("Failed to Import Presets", msg)
        except BaseException as e:
            print(f"[error] Failed to load custom presets: {str(e)}")
            self.alert.show_warning("Failed to Load Presets", f"Lyrebird failed to load custom presets, your presets.toml file is most likely malformed. See the console for further details.\n\nPresets file location: {config.presets_path}")

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
        self.preset_buttons = self.create_flowbox_items(self.flowbox)
        self.preset_buttons[9].set_sensitive(False)

        self.vbox.pack_start(self.hbox_toggle, False, False, 5)
        self.vbox.pack_start(self.hbox_pitch, False, False, 5)
        self.vbox.pack_start(self.effects_label, False, False, 5)
        self.vbox.pack_end(self.flowbox, True, True, 0)

        self.add(self.vbox)

    def create_flowbox_items(self, flowbox):
        buttons = []
        for preset in state.loaded_presets:
            button = Gtk.Button()
            button.set_size_request(80, 80)
            buttons.append(button)

            button.set_label(preset.name)
            button.connect('clicked', self.preset_clicked)
            flowbox.add(button)
        return buttons

    # Event handlers
    def about_clicked(self, button):
        about = Gtk.AboutDialog()
        about.set_program_name('Lyrebird Voice Changer')
        about.set_version("v1.2.0")
        about.set_copyright('Copyright (c) 2020-2023 megabytesofrem, Harry Stanton')
        about.set_comments('Simple and powerful voice changer for Linux, written in Python & GTK.')
        about.set_logo(GdkPixbuf.Pixbuf.new_from_file('icon.png'))

        about.run()
        about.destroy()

    def get_current_present(self):
        default_preset = state.loaded_presets[9]
        return state.current_preset or default_preset

    def start_voice_changer(self):
        preset = self.get_current_present()
        pitch = self.pitch_scale.get_value()
        state.audio.run_sox(pitch, preset, state.config.buffer_size)

    def stop_voice_changer(self):
        state.audio.kill_sox()
        state.audio.unload_pa_modules()

    def toggle_activated(self, switch, gparam):
        if switch.get_active():
            # Load module-null-sink
            state.audio.load_pa_modules()

            # Kill the sox process
            state.audio.kill_sox()

            # Use the default preset, which is "Man" if the loaded preset is not found.
            
            self.start_voice_changer()
        else:
            self.stop_voice_changer()

    def pitch_scale_moved(self, event):
        if self.toggle_switch.get_active():
            state.audio.kill_sox()
            self.start_voice_changer()

    def preset_clicked(self, button):
        # Use a filter to find the currently selected preset
        current_preset = list(filter(lambda p: p.name == button.props.label, state.loaded_presets))[0]
        state.current_preset = current_preset

        for preset_button in self.preset_buttons:
            preset_button.set_sensitive(True)
        button.set_sensitive(False)

        if current_preset.pitch_value != None:
            # Set the pitch of the slider
            self.pitch_scale.set_value(float(current_preset.pitch_value))
        
        if self.toggle_switch.get_active():
            state.audio.kill_sox()
            self.start_voice_changer()

    def close(self, *args):
        state.audio.kill_sox()
        state.audio.unload_pa_modules()

        self.lock_file.close()
        lock.destroy_lock()
        
        Gtk.main_quit()

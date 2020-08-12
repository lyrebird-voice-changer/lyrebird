#!/bin/python

import gi
import subprocess

gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, Gdk, GdkPixbuf

import src.effects as effects
import src.state as state
from src.effects import Preset

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

        about_btn = Gtk.Button()
        about_btn.props.image = Gtk.Button.new_from_icon_name('help-about-symbolic', Gtk.IconSize.BUTTON)
        about_btn.connect('clicked', self.about_clicked)
        headerbar.pack_start(about_btn)

        open_pavucontrol_btn = Gtk.Button()
        open_pavucontrol_btn.props.image = Gtk.Button.new_from_icon_name('audio-x-generic-symbolic', Gtk.IconSize.BUTTON)
        open_pavucontrol_btn.connect('clicked', self.open_pavucontrol_clicked)
        headerbar.pack_start(open_pavucontrol_btn)

        self.set_titlebar(headerbar)

        # Unload the null sink module if there is one from last time.
        # The only reason there would be one already, is if the application was closed without
        # toggling the switch to off.
        subprocess.call(['pactl', 'unload-module', 'module-null-sink'])

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

        # Flowbox containing the effects
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
        effects.effect_presets = effects.load_presets()

        for effect in effects.effect_presets:
            button = Gtk.Button()
            button.set_size_request(80, 80)

            button.set_label(effect.name)
            button.connect('clicked', self.effect_clicked)
            flowbox.add(button)

    # Event handlers
    def about_clicked(self, button):
        about = Gtk.AboutDialog()
        about.set_program_name('Lyrebird')
        about.set_copyright('(c) charlotte 2020')
        about.set_comments('Simple and powerful voice changer for Linux, written in GTK 3')
        about.set_logo(GdkPixbuf.Pixbuf.new_from_file('icon.png'))

        about.run()
        about.destroy()

    def open_pavucontrol_clicked(self, button):
        subprocess.call(['pavucontrol'])

    def toggle_activated(self, switch, gparam):
        if switch.get_active():
            # Load module-null-sink
            sink = subprocess.check_call('pactl load-module module-null-sink'.split(' '))
            state.sink = sink

            # Kill the sox process
            subprocess.call('pkill sox'.split(' '))

            # Multiply the pitch shift scale value by the multiplier and feed it to sox
            pitch_shift = self.pitch_scale.get_value() * sox_multiplier

            command = f'sox --buffer 1024 -q -t pulseaudio default -t pulseaudio null pitch {pitch_shift}'
            sox_process = subprocess.Popen(command.split(' '))
        else:
            dialog = Gtk.MessageDialog(
                transient_for=self,
                message_type=Gtk.MessageType.INFO,
                buttons=Gtk.ButtonsType.OK,
                text='Unloaded module-null-sink'
            )

            dialog.format_secondary_text('PulseAudio Null Output sink has been unloaded. Lyrebird will no longer work.')

            dialog.run()
            dialog.destroy()

            # Unload module-null-sink if there is a sink loaded
            if state.sink != -1:
                subprocess.call('pactl unload-module module-null-sink'.split(' '))

            # Kill the sox process
            subprocess.call('pkill sox'.split(' '))

    def pitch_scale_moved(self, event):
        global sox_multiplier
        # FIXME: Very hacky code, we repeatedly kill sox, grab the new value to pitch shift
        # by, and then restart the process. Not sure if theres a better way to do this but there
        # has to be lol.

        # Kill the sox process
        subprocess.call('pkill sox'.split(' '))

        # Only allow adjusting the pitch if the preset doesn't override the pitch
        if state.current_preset is not None:
            if not state.current_preset.override_pitch:
                # Multiply the pitch shift scale value by the multiplier and feed it to sox
                command = self.build_sox_command(state.current_preset)
                sox_process = subprocess.Popen(command.split(' '))
    
    def build_sox_command(self, preset):
        effects = []

        if preset.pitch_value != 'default':
            pass
        if preset.pitch_value == 'scale':
            effects.append(f'pitch {float(self.pitch_scale.get_value()) * sox_multiplier}')
        else:
            effects.append(f'pitch {float(preset.pitch_value) * sox_multiplier}')

        if preset.downsample_amount != 'none':
            effects.append(f'downsample {int(preset.downsample_amount)}')
        else:
            # Append downsample of 1, to fix a bug where the downsample isn't being reverted
            # when we disable the effect with it on.
            effects.append('downsample 1')

        sox_effects = ' '.join(effects)
        command = f'sox --buffer 1024 -q -t pulseaudio default -t pulseaudio null {sox_effects}'

        return command

    def effect_clicked(self, button):
        global sox_multiplier
        subprocess.call(['pkill', 'sox'])


        # TODO: Replace this so its more efficient
        current_preset = list(filter(lambda e: e.name == button.props.label, effects.effect_presets))[0]
        command = self.build_sox_command(current_preset)
    
        if current_preset.override_pitch:
            # Set the pitch of the slider
            self.pitch_scale.set_value(float(current_preset.pitch_value))
            self.pitch_scale.set_sensitive(False)
        else:
            self.pitch_scale.set_sensitive(True)

        state.current_preset = current_preset
        sox_process = subprocess.Popen(command.split(' '))
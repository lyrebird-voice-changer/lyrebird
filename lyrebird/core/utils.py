import subprocess
import sys

import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gdk, GdkPixbuf, Gtk

import lyrebird.core.config as config
import lyrebird.core.state as state



def key_or_default(key, dict, default):
    return dict[key] if key in dict else default

def build_sox_command(preset, config_object=None, scale_object=None):
    '''
    Builds and returns a sox command from a preset object.
    '''
    effects = []

    # Pitch shift
    pitch_multiplier = 100
    if preset.pitch_value == 'default':
        pitch_shift = 0
    if preset.pitch_value == 'scale':
        pitch_shift = float(scale_object.get_value()) * pitch_multiplier
    else:
        pitch_shift = float(preset.pitch_value) * pitch_multiplier
    effects.append(f'pitch {pitch_shift}')

    # Volume boosting
    if preset.volume_boost == 'default' or preset.volume_boost == None:
        volume_boost = 0
    else:
        volume_boost = int(preset.volume_boost)
    effects.append(f'vol {volume_boost}dB')

    # Downsampling
    if preset.downsample_amount != 'none':
        downsample_amount = int(preset.downsample_amount)
    else:
        # Append downsample of 1 to fix a bug where the downsample isn't being reverted
        # when we disable the effect with it on.
        downsample_amount = 1
    effects.append(f'downsample {downsample_amount}')

    sox_effects = ' '.join(effects)
    command = f'sox --buffer {config_object.buffer_size or 1024} -q -t pulseaudio default -t pulseaudio Lyrebird-Output {sox_effects}'

    return command

def unload_pa_modules(check_state=False):
    '''
    Unloads both the PulseAudio null output.
    If `check_state` is `True`, then this will check if `state.sink` is not -1.
    '''

    # Unload if we don't care about state, or we do and there is a sink loaded
    if not check_state or state.sink != -1:
        subprocess.call('pacmd unload-module module-null-sink'.split(" "))
        subprocess.call('pacmd unload-module module-remap-source'.split(' '))

def show_error_message(msg, parent, title):
    '''
    Create an error message dialog with string message.
    '''
    dialog = Gtk.MessageDialog(
        parent         = None,
        type           = Gtk.MessageType.ERROR,
        buttons        = Gtk.ButtonsType.OK,
        message_format = msg)
    dialog.set_transient_for(parent)
    dialog.set_title(title)

    dialog.show()
    dialog.run()
    dialog.destroy()
    sys.exit(1)

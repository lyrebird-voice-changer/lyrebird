import subprocess
import app.core.state as state
import app.core.config as config
import sys
import fcntl

from pathlib import Path

import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, Gdk, GdkPixbuf


def key_or_default(key, dict, default):
    return dict[key] if key in dict else default

def build_sox_command(preset, config_object=None, scale_object=None):
    '''
    Builds and returns a sox command from a preset object
    '''
    multiplier = 100
    effects = []


    # Pitch shift
    if preset.pitch_value == 'default':
        effects.append('pitch 0')
    if preset.pitch_value == 'scale':
        effects.append(f'pitch {float(scale_object.get_value()) * multiplier}')
    else:
        effects.append(f'pitch {float(preset.pitch_value) * multiplier}')

    # Volume boosting
    if preset.volume_boost == 'default' or preset.volume_boost == None:
        effects.append('vol 0dB')
    else:
        effects.append(f'vol {int(preset.volume_boost)}dB')

    # Downsampling
    if preset.downsample_amount != 'none':
        effects.append(f'downsample {int(preset.downsample_amount)}')
    else:
        # Append downsample of 1 to fix a bug where the downsample isn't being reverted
        # when we disable the effect with it on.
        effects.append('downsample 1')

    sox_effects = ' '.join(effects)
    command = f'sox --buffer {config_object.buffer_size or 1024} -q -t pulseaudio default -t pulseaudio Lyrebird-Output {sox_effects}'

    return command

def unload_pa_modules(check_state=False):
    '''
    Unloads both the PulseAudio null output
    If `check_state` is `True`, then this will check if `state.sink` is not -1.
    '''

    # Unload if we don't care about state, or we do and there is a sink loaded
    if not check_state or state.sink != -1:
        subprocess.call('pactl unload-module module-null-sink'.split(" "))
        subprocess.call('pactl unload-module module-remap-source'.split(' '))

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

lock_file_path = Path(Path('/tmp') / 'lyrebird.lock')
def place_lock():
    '''
    Places a lockfile file in the user's home directory to prevent
    two instances of Lyrebird running at once.

    Returns lock file to be closed before application close, if
    `None` returned then lock failed and another instance of
    Lyrebird is most likely running.
    '''
    lock_file = open(lock_file_path, 'w')
    try:
        fcntl.flock(lock_file, fcntl.LOCK_EX | fcntl.LOCK_NB)
    except:
        return None
    return lock_file

def destroy_lock():
    '''
    Destroy the lock file. Should close lock file before running.
    '''
    if lock_file_path.exists():
        lock_file_path.unlink()

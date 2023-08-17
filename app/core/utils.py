import subprocess
import app.core.state as state
import app.core.config as config
import sys
import fcntl

from pathlib import Path

import gi
gi.require_version('Gtk', '4.0')
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
        
def parse_pactl_info_short(lines):
    '''
    Parses `pactl info short` into tuples containing the module ID,
    the module type and the attributes of the module. It is designed
    only for named modules and as such junk data may be included in
    the returned list.
    
    Returns an array of tuples that take the form:
        (module_id (str), module_type (str), attributes (attribute tuples))
      
    The attribute tuples:
        (key (str), value (str))
        
    An example output might look like:
        [
            ( '30', 'module-null-sink', [('sink_name', 'Lyrebird-Output')] ),
            ( '31', 'module-remap-source', [('source_name', 'Lyrebird-Input'), ('master', 'Lyrebird-Output.monitor')] )
        ]
    '''
    data = []
    split_lines = lines.split("\n")
    for line in split_lines:
        info = line.split("\t")
        if len(info) <= 2:
            continue
        
        if info[2] and len(info[2]) > 0:
            key_values = list(map(lambda key_value: tuple(key_value.split("=")), info[2].split(" ")))
            data.append((info[0], info[1], key_values))
        else:
            data.append((info[0], info[1], []))
    return data
    
def get_sink_name(tuple):
    print(tuple)
    if tuple[0] == "sink_name":
        return tuple[1]
    elif tuple[0] == "source_name":
        return tuple[1]
    else:
        return None

def unload_pa_modules():
    '''
    Unloads all Lyrebird null sinks.
    '''
    pactl_list = subprocess.run(["pactl", "list", "short"], capture_output=True, encoding="utf8")
    stdout = pactl_list.stdout
    modules = parse_pactl_info_short(stdout)
    lyrebird_module_ids = []
    for module in modules:
        if len(module) < 3:
            continue;
        if len(module[2]) < 1:
            continue;

        # print(module)
        if module[1] == "module-null-sink":
            sink_name = get_sink_name(module[2][0])
            if sink_name == "Lyrebird-Output":
                lyrebird_module_ids.append(module[0])
        elif module[1] == "module-remap-source":
            sink_name = get_sink_name(module[2][0])
            if sink_name == "Lyrebird-Input":
                lyrebird_module_ids.append(module[0])

    for id in lyrebird_module_ids:
            subprocess.run(["pactl", "unload-module", str(id)])

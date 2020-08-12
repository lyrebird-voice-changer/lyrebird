import subprocess
import src.core.state as state
import src.core.config as config

def build_sox_command(preset, config_object=None, scale_object=None):
    '''
    Builds and returns a sox command from a preset object
    '''
    multiplier = 100
    effects = []

    if preset.pitch_value == 'default':
        effects.append('pitch 0')
    if preset.pitch_value == 'scale':
        effects.append(f'pitch {float(scale_object.get_value()) * multiplier}')
    else:
        effects.append(f'pitch {float(preset.pitch_value) * multiplier}')

    if preset.downsample_amount != 'none':
        effects.append(f'downsample {int(preset.downsample_amount)}')
    else:
        # Append downsample of 1 to fix a bug where the downsample isn't being reverted
        # when we disable the effect with it on.
        effects.append('downsample 1')

    sox_effects = ' '.join(effects)
    command = f'sox --buffer {config_object.buffer_size or 1024} -q -t pulseaudio default -t pulseaudio null {sox_effects}'

    return command

def kill_sink(check_state=False):
    '''
    Unloads both the PulseAudio null output, and kills the sox process
    If `check_state` is `True`, then this will check if `state.sink` is not -1.
    '''

    # Unload module-null-sink if there is a sink loaded
    if check_state:
        if state.sink != -1:
            subprocess.call('pactl unload-module module-null-sink'.split(' '))
    else:
        # Just unload it anyways, we don't care about the sinks state
        subprocess.call('pactl unload-module module-null-sink'.split(' '))

    # Kill the sox process
    subprocess.call('pkill sox'.split(' '))
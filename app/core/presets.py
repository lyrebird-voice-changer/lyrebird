import toml
import pathlib
from pathlib import Path

from app.core.utils import key_or_default
import app.core.config as config

class Preset:
    def __init__(self,
                name,
                pitch_value,
                downsample_amount,
                override_pitch,
                volume_boost,
                custom_sox_command):
        self.name = name
        self.pitch_value = pitch_value
        self.downsample_amount = downsample_amount
        self.override_pitch = override_pitch
        self.volume_boost = volume_boost
        self.custom_sox_command = custom_sox_command

    @staticmethod
    def from_dict(d):
        '''
        Constructs a `Preset` instance from a dictionary item and returns it
        '''

        # pylint: disable=bad-continuation
        return Preset(
                name=d['name'],
                pitch_value=d['pitch_value'],
                downsample_amount=key_or_default(key='downsample_amount',  dict=d, default='1'),
                override_pitch=key_or_default(key='override_pitch_slider', dict=d, default='false'),
                volume_boost=key_or_default(key='volume_boost', dict=d, default='0'),
                custom_sox_command = key_or_default(key='custom_sox_command', dict=d, default='none')
        )

def load_presets():
    '''
    Loads presets from ~/.config/lyrebird/presets.toml and returns
    a list of `Preset` objects from the file
    '''

    create_presets()
    presets = []

    path = config.presets_path
    with open(path, 'r') as f:
        presets_data = toml.loads(f.read())['presets']
        for item in presets_data:
            preset = Preset.from_dict(item)
            presets.append(preset)

    return presets

PRESETS_CONTENTS = '''
# Effect presets are defined in presets.toml
# The following parameters are available for presets

# name = Preset name, will be displayed in the GUI
# pitch_value = The pitch value of the preset, if you want to be able to adjust this use "scale"
# downsample_amount = The amount of downsampling to do, set as "none" if you don't want any
# override_pitch_slider = Whether the preset overrides the pitch slider or not

# custom_sox_command = enter commands directly from the sox utility. can be left undefiened

[[presets]]
name = "Cum"
pitch_value = "-1.5"
downsample_amount = "none"
override_pitch_slider = true

[[presets]]
name = "Woman"
pitch_value = "2.5"
downsample_amount = "none"
override_pitch_slider = true

[[presets]]
name = "Boy"
pitch_value = "1.25"
downsample_amount = "none"
override_pitch_slider = true

[[presets]]
name = "Girl"
pitch_value = "2.8"
downsample_amount = "none"
override_pitch_slider = true

[[presets]]
name = "Darth Vader"
pitch_value = "-6"
downsample_amount = "none"
override_pitch_slider = true

[[presets]]
name = "Chipmunk"
pitch_value = "10.0"
downsample_amount = "none"
override_pitch_slider = true

[[presets]]
name = "Russian Mic"
pitch_value = "scale"
downsample_amount = "8"
override_pitch_slider = false
volume_boost = "8"

[[presets]]
name = "Radio"
pitch_value = "scale"
downsample_amount = "6"
override_pitch_slider = false
volume_boost = "5"

[[presets]]
name = "Megaphone"
pitch_value = "scale"
downsample_amount = "2"
override_pitch_slider = false
volume_boost = "8"

[[presets]]
name = "Custom"
pitch_value = "scale"
downsample_amount = "none"
override_pitch_slider = false

[[presets]]
name = "Muffled - thin wall"
pitch_value = "scale"
downsample_amount = "none"
override_pitch_slider = false
custom_sox_command = "lowpass 400"

[[presets]]
name = "Muffled - thick wall"
pitch_value = "scale"
downsample_amount = "none"
override_pitch_slider = false
custom_sox_command = "lowpass 200"

[[presets]]
name = "Old telephone"
pitch_value = "scale"
downsample_amount = "none"
override_pitch_slider = false
custom_sox_command = "lowpass 5000 highpass 500"

[[presets]]
name = "Echo - (large buffer)"
pitch_value = "scale"
downsample_amount = "none"
override_pitch_slider = false
custom_sox_command = "echos 0.8 0.7 40 0.25 63 0.3"

'''

def create_presets():
    config.create_config_dir()
    if not config.presets_path.exists():
        with open(config.presets_path, 'w') as f:
            f.write(PRESETS_CONTENTS)

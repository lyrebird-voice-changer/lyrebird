import toml
import pathlib
from pathlib import Path

from app.core.utils import key_or_default
import app.core.config as config

class Preset:
    def __init__(self,
                name,
                effects):
        self.name = name
        self.effects = effects

    @staticmethod
    def from_dict(d):
        '''
        Constructs a `Preset` instance from a dictionary item and returns it
        '''
        name = d.pop('name')

        # pylint: disable=bad-continuation
        return Preset(
                name=name,
                effects=d
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

[[presets]]
name = "Man"
pitch = [-150]

[[presets]]
name = "Woman"
pitch = [250]

[[presets]]
name = "Boy"
pitch = [125]

[[presets]]
name = "Girl"
pitch = [280]

[[presets]]
name = "Darth Vader"
pitch = [-600]

[[presets]]
name = "Chipmunk"
pitch = [1000]

[[presets]]
name = "Russian Mic"
downsample = [8]
vol = ["8dB"]

[[presets]]
name = "Radio"
downsample = [6]
vol = ["5dB"]

[[presets]]
name = "Megaphone"
downsample = [2]
vol = ["8dB"]

[[presets]]
name = "Custom"
'''

def create_presets():
    config.create_config_dir()
    if not config.presets_path.exists() or True:
        with open(config.presets_path, 'w') as f:
            f.write(PRESETS_CONTENTS)

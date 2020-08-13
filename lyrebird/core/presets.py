import toml
import pathlib
from pathlib import Path
import lyrebird.core.config as config

class Preset:
    def __init__(self, name, pitch_value, downsample_amount, override_pitch):
        self.name = name
        self.pitch_value = pitch_value
        self.downsample_amount = downsample_amount
        self.override_pitch = override_pitch

    @staticmethod
    def from_dict(d):
        '''
        Constructs a `Preset` instance from a dictionary item and returns it
        '''

        # pylint: disable=bad-continuation
        return Preset(
                name=d['name'],
                pitch_value=d['pitch_value'],
                downsample_amount=d['downsample_amount'],
                override_pitch=d['override_pitch_slider']
        )

def load_presets():
    '''
    Loads presets from ~/.config/lyrebird/presets.toml and returns
    a list of `Preset` objects from the file
    '''

    presets = []

    path = config.get_config_path('presets.toml')
    with open(path, 'r') as f:
        presets_data = toml.loads(f.read())['presets']
        for item in presets_data:
            preset = Preset.from_dict(item)
            presets.append(preset)

    return presets


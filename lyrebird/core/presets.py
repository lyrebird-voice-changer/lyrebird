import toml
import pathlib
from pathlib import Path

from lyrebird.core.utils import key_or_default
import lyrebird.core.config as config

class Preset:
    def __init__(self, 
                name,
                pitch_value,
                downsample_amount,
                override_pitch,
                volume_boost):
        self.name = name
        self.pitch_value = pitch_value
        self.downsample_amount = downsample_amount
        self.override_pitch = override_pitch
        self.volume_boost = volume_boost

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
                volume_boost=key_or_default(key='volume_boost', dict=d, default='0')
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

import toml
import pathlib
from pathlib import Path

import app.core.config as config

def key_or_default(key, dict, default):
    return dict[key] if key in dict else default

class Preset:
    def __init__(self,
                name,
                pitch_value,
                downsample_amount,
                volume_boost):
        self.name = name
        self.pitch_value = pitch_value
        self.downsample_amount = downsample_amount
        self.volume_boost = volume_boost

def load_presets():
    '''
    Loads presets from ~/.config/lyrebird/presets.toml and returns
    a list of `Preset` objects from the file
    '''

    # create_presets()
    presets = []
    failed = []

    path = config.presets_path
    with open(path, 'r') as f:
        presets_data = toml.loads(f.read())['presets']
        for item in presets_data:
            # name
            if "name" not in item:
                print("[error] Preset missing name, skipping")
                continue
            name = item["name"]
            # pitch value
            pitch_value = None
            if "pitch_value" in item and item["pitch_value"] != "scale":
                try:
                    pitch_value = float(item["pitch_value"])
                except ValueError:
                    failed.append(name)
                    print(f"[error] Preset '{name}' failed to load: invalid pitch value '{item['pitch_value']}'")
                    continue
            # downsample
            downsample_amount = None
            if "downsample_amount" in item and item["downsample_amount"] != "none":
                try:
                    downsample_amount = int(item["downsample_amount"])
                except ValueError:
                    failed.append(name)
                    print(f"[error] Preset '{name}' failed to load: invalid downsample value '{item['downsample_amount']}'")
                    continue
            # volume boost
            volume_boost = None
            if "volume_boost" in item:
                if item["volume_boost"] != "none":
                    try:
                        volume_boost = int()
                    except ValueError:
                        failed.append(name)
                        print(f"[error] Preset '{name}' failed to load: invalid volume boost value '{item['volume_boost']}'")
                        continue
            preset = Preset(name=name,
                pitch_value=pitch_value,
                downsample_amount=downsample_amount,
                volume_boost=volume_boost)
            presets.append(preset)

    return { "presets": presets, "failed": failed }

DEFAULT_PRESETS = [
    Preset("Man", -1.5, None, None),
    Preset("Woman", 2.5, None, None),
    Preset("Boy", 1.25, None, None),
    Preset("Girl", 2.8, None, None),
    Preset("Darth Vader", -6.0, None, None),
    Preset("Chipmunk", 10.0, None, None),
    Preset("Russian Mic", None, 8, 0),
    Preset("Radio", None, 6, 0),
    Preset("Megaphone", None, 2, 0),
    Preset("Reset", 0.0, None, None)
]

PRESETS_CONTENTS = '''
# Effect presets are defined in presets.toml
# The following parameters are available for presets

# name = Preset name, will be displayed in the GUI
# pitch_value = The pitch value of the preset, if you want to be able to adjust this use "scale"
# downsample_amount = The amount of downsampling to do, set as "none" if you don't want any
# override_pitch_slider = Whether the preset overrides the pitch slider or not

[[presets]]
name = "Man"
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
name = "Reset"
pitch_value = "0"
downsample_amount = "none"
override_pitch_slider = true
'''

def create_presets():
    config.create_config_dir()
    if not config.presets_path.exists():
        with open(config.presets_path, 'w') as f:
            f.write(PRESETS_CONTENTS)

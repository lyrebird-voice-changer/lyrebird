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

    def matches(self, y):
        name = self.name == y.name
        pitch = self.pitch_value == y.pitch_value
        downsample = self.downsample_amount == y.downsample_amount
        volume = self.volume_boost == y.volume_boost

        return name and pitch and downsample and volume

    def dictionary(self):
        dictionary = { "name": self.name }
        if self.pitch_value is not None:
            dictionary["pitch_value"] = self.pitch_value
        if self.downsample_amount is not None:
            dictionary["downsample_amount"] = self.downsample_amount
        if self.volume_boost is not None:
            dictionary["volume_boost"] = self.volume_boost
        return dictionary

DEFAULT_PRESETS = [
    Preset("Man", -1.5, None, None),
    Preset("Woman", 2.5, None, None),
    Preset("Boy", 1.25, None, None),
    Preset("Girl", 2.8, None, None),
    Preset("Darth Vader", -6.0, None, None),
    Preset("Chipmunk", 10.0, None, None),
    Preset("Bad Mic", None, 8, 0),
    Preset("Radio", None, 6, 0),
    Preset("Megaphone", None, 2, 0),
    Preset("Off", 0.0, None, None)
]

LEGACY_PRESETS = [
    Preset("Man", -1.5, None, None),
    Preset("Woman", 2.5, None, None),
    Preset("Boy", 1.25, None, None),
    Preset("Girl", 2.8, None, None),
    Preset("Darth Vader", -6.0, None, None),
    Preset("Chipmunk", 10.0, None, None),
    Preset("Russian Mic", None, 8, 8),
    Preset("Radio", None, 6, 5),
    Preset("Megaphone", None, 2, 8),
    Preset("Custom", None, None, None)
]

PRESETS_TOML_HEADER='''# Effect presets are defined in presets.toml
# The following parameters are available for presets

# name: Preset name, will be displayed in the GUI
# pitch_value: The pitch value of the preset, float value between -10.0 to 10.0. Omit if pitch value should not be affected from slider value.
# downsample_amount Downsample by an integer factor.
# volume_boost: Amount in dB to boost the audio. Can be negative to make the audio quieter.

# e.g.
# [[presets]]
# name = "Bad Mic"
# pitch_value = "-1.5"
# downsample_amount = "8"
# volume_boost = "8"
'''

def load_presets():
    '''
    Loads presets from ~/.config/lyrebird/presets.toml and returns
    a list of `Preset` objects from the file
    '''

    # create_presets()
    presets = []
    failed = []

    path = config.presets_path

    if not config.presets_path.exists():
        create_presets()
        return { "presets": [], "failed": [] }

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
                    pitch_value = min(max(pitch_value, -10), 10)
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
                        volume_boost = int(item["volume_boost"])
                    except ValueError:
                        failed.append(name)
                        print(f"[error] Preset '{name}' failed to load: invalid volume boost value '{item['volume_boost']}'")
                        continue
            preset = Preset(name=name,
                pitch_value=pitch_value,
                downsample_amount=downsample_amount,
                volume_boost=volume_boost)
            presets.append(preset)

    custom_presets = []
    contains_legacy = False
    for preset in presets:
        legacy_match = False
        for legacy_preset in LEGACY_PRESETS:
            legacy_match = legacy_preset.matches(preset)
            if legacy_match:
                break
        if not legacy_match:
            custom_presets.append(preset)
        else:
            contains_legacy = True

    if contains_legacy:
        print(f"[info] Config file ({path}) contains legacy presets, writing new file with {len(custom_presets)} custom preset(s)")
        create_presets(custom_presets)
        
    return { "presets": custom_presets, "failed": failed }

def create_presets(presets=[]):
    config.create_config_dir()

    if config.presets_path.exists():
        old_file_data = None
        with open(config.presets_path, "r") as f:
            old_file_data = f.read()
        with open(config.presets_old_path, "w") as f:
            f.write(old_file_data)

    with open(config.presets_path, "w") as f:
        f.write(PRESETS_TOML_HEADER + "\n")

        presets = map(lambda x: x.dictionary(), presets)
        presets = list(presets)
        toml_data = toml.dumps({ "presets": presets })
        f.write(toml_data)

import toml

from dataclasses import dataclass
from pathlib import Path

@dataclass
class Configuration:
    buffer_size: int = 128

config_dir = Path(Path.home() / ".config" / "lyrebird")
config_path = Path(config_dir / "config.toml")
presets_path = Path(config_dir / "presets.toml")
presets_old_path = Path(config_dir / "presets.toml.old")

def load_config():
    '''
    Loads the config file located at ~/.config/lyrebird/config.toml, parses it
    and returns a `Configuration` object.
    '''
    create_config()

    config = {}
    path = config_path
    with open(path, 'r') as f:
        config = toml.loads(f.read())['config'][0]

    return Configuration(buffer_size=int(config['buffer_size']))

def create_config_dir():
    config_dir.mkdir(parents=True, exist_ok=True)

CONFIG_CONTENTS = '''
# Configuration file for Lyrebird
# The following parameters are configurable
# buffer_size = The buffer size to use for sox. Higher = better quality, at
# the cost of higher latency. Default value is 128
[[config]]
buffer_size = 128
'''

def create_config():
    create_config_dir()
    if not config_path.exists():
        with open(config_path, 'w') as f:
            f.write(CONFIG_CONTENTS)

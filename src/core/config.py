import toml
import pathlib
from dataclasses import dataclass
from pathlib import Path

@dataclass
class Configuration:
    buffer_size: int

def load_config():
    '''
    Loads the config file located at ~/.config/lyrebird/config.toml, parses it
    and returns a `Configuration` object.
    '''
    
    config = {}

    path = Path(Path.home() / '.config' / 'lyrebird' / 'config.toml')
    with open(path, 'r') as f:
        config = toml.loads(f.read())['config'][0]

    return Configuration(buffer_size=int(config['buffer_size']))
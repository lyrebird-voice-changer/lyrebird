'''
Provides functionality for loading and parsing config files
'''

import toml
import pathlib
from dataclasses import dataclass
from pathlib import Path

@dataclass
class Configuration:
    buffer_size: int

def load_config():
    config = {}

    path = Path(Path.home() / '.config' / 'lyrebird' / 'config.toml')
    with open(path, 'r') as f:
        config = toml.loads(f.read())['config'][0]

    return Configuration(buffer_size=int(config['buffer_size']))
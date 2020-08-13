import toml
import pathlib
from dataclasses import dataclass
from pathlib import Path
import lyrebird.core.config as config

class ConfigNotFoundError(Exception):
    pass

@dataclass
class Configuration:
    buffer_size: int

def get_config_path(file):
    '''
    Gets the requested config file, raises `ConfigNotFoundError` if none found
    '''
    global_path = Path(Path('/etc') / 'lyrebird' / file)
    user_path = Path(Path.home() / '.config' / 'lyrebird' / file)

    if user_path.exists():
        return user_path
    elif global_path.exists():
        return global_path
    else:
        raise ConfigNotFoundError

def load_config():
    '''
    Loads the config file located at ~/.config/lyrebird/config.toml, parses it
    and returns a `Configuration` object.
    '''
    config = {}

    path = get_config_path('config.toml')
    with open(path, 'r') as f:
        config = toml.loads(f.read())['config'][0]

    return Configuration(buffer_size=int(config['buffer_size']))
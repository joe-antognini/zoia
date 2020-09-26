"""Module to manage configuration of `zoia`.

By default `zoia`'s configuration files will live in `$XDG_CONFIG_HOME/zoia/`.
If the user has not set `$XDG_CONFIG_HOME`, `zoia` will use the default
configuration directory of `$HOME/.config/zoia/`.

"""

import os
from dataclasses import dataclass
from enum import Enum

import yaml

ZOIA_METADATA_FILENAME = 'metadata.json'


class ZoiaBackend(Enum):
    JSON = 'json'
    REDIS = 'redis'
    SQLITE = 'sqlite'


@dataclass
class ZoiaConfig:
    library_root: str
    db_root: str = None
    backend: ZoiaBackend = ZoiaBackend.JSON

    def __post_init__(self):
        if self.db_root is None:
            self.db_root = _get_db_root()

    def to_dict(self):
        d = {
            elem: getattr(self, elem)
            for elem in self.__dataclass_fields__.keys()
        }

        d['backend'] = d['backend'].value

        return d


def get_config_filepath():
    """Return the filepath of the configuration file."""
    default_config_root = os.path.join(os.path.expanduser('~'), '.config')
    config_root = os.getenv('XDG_CONFIG_HOME', default=default_config_root)
    return os.path.join(config_root, 'zoia/config.yaml')


def load_config(config_filepath=None):
    """Load the zoia configuration file if it exists."""
    if config_filepath is None:
        config_filepath = get_config_filepath()

    if not os.path.exists(config_filepath):
        return None

    try:
        with open(config_filepath) as fp:
            config = yaml.safe_load(fp)
    except (yaml.scanner.ScannerError, yaml.parser.ParserError):
        raise RuntimeError(
            f'Unable to parse configuration file at {config_filepath}.'
        )

    if not isinstance(config, dict):
        raise RuntimeError(
            f'Found existing configuration file at {config_filepath} but type '
            f'must be dict and found type {type(config)}.'
        )

    if 'library_root' not in config:
        raise KeyError(
            'library_root key must be present in configuration file.'
        )

    return ZoiaConfig(
        library_root=config['library_root'],
        db_root=_get_db_root(),
        backend=ZoiaBackend(config.get('backend', 'json')),
    )


def save_config(config: ZoiaConfig, config_filepath: str = None):
    """Save the given configuration data."""
    if not isinstance(config, ZoiaConfig):
        raise TypeError(
            f'Given configuration must be a dictionary but got type '
            f'{type(config)}.'
        )

    if config_filepath is None:
        config_filepath = get_config_filepath()

    zoia_config_root = os.path.dirname(config_filepath)
    os.makedirs(zoia_config_root, exist_ok=True)
    with open(config_filepath, 'w') as fp:
        yaml.safe_dump(config.to_dict(), fp)


def _get_db_root():
    """Find the directory with the database."""
    default_data_dir = os.path.join(os.getenv('HOME'), '.local/share/zoia')
    return os.getenv('XDG_DATA_HOME', default=default_data_dir)

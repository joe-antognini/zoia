"""Module to manage configuration of `zoia`.

By default `zoia`'s configuration files will live in `$XDG_CONFIG_HOME/zoia/`.
If the user has not set `$XDG_CONFIG_HOME`, `zoia` will use the default
configuration directory of `$HOME/.config/zoia/`.

"""

import os

import yaml

ZOIA_METADATA_FILENAME = '.metadata.json'


def get_config_filepath():
    """Return the filepath of the configuration file."""
    default_config_root = os.path.join(os.path.expanduser('~'), '.config')
    config_root = os.getenv('XDG_CONFIG_HOME', default=default_config_root)
    return os.path.join(config_root, 'zoia/config.yaml')


def load_config():
    """Load the zoia configuration file if it exists."""
    config_filepath = get_config_filepath()
    if not os.path.exists(config_filepath):
        return {}

    with open(config_filepath) as fp:
        config = yaml.safe_load(fp)

    if not isinstance(config, dict):
        raise RuntimeError(
            f'Found existing configuration file at {config_filepath} but type '
            f'must be dict and found type {type(config)}.'
        )

    return config


def save_config(new_config):
    """Save the given configuration data."""
    if not isinstance(new_config, dict):
        raise TypeError(
            f'Given configuration must be a dictionary but got type '
            f'{type(new_config)}.'
        )

    old_config = load_config()
    merged_config = {**old_config, **new_config}
    config_filepath = get_config_filepath()
    zoia_config_root = os.path.dirname(config_filepath)
    os.makedirs(zoia_config_root, exist_ok=True)
    with open(config_filepath, 'w') as fp:
        yaml.safe_dump(merged_config, fp)


def get_library_root():
    """Find the root directory of the `zoia` library."""
    config = load_config()
    return config['directory'] if config and 'directory' in config else None


def set_library_root(library_root):
    """Set the root directory of the `zoia` library."""
    config = {'directory': library_root}
    save_config(config)

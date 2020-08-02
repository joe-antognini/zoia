"""Module to manage configuration of `zoia`."""

import os

import yaml

ZOIA_CONFIG_ROOT = os.path.join(os.path.expanduser('~'), '.local/share/zoia')
ZOIA_CONFIG_FILENAME = 'config.yaml'
ZOIA_CONFIG_FILEPATH = os.path.join(ZOIA_CONFIG_ROOT, ZOIA_CONFIG_FILENAME)
ZOIA_METADATA_FILENAME = '.metadata.json'


def get_library_root(config_filepath=ZOIA_CONFIG_FILEPATH):
    """Find the root directory of the `zoia` library."""
    if not os.path.exists(config_filepath):
        return None

    with open(config_filepath) as fp:
        config = yaml.safe_load(fp)

    return config['directory'] if config and 'directory' in config else None


def set_library_root(library_root, config_filepath=ZOIA_CONFIG_FILEPATH):
    """Set the root directory of the `zoia` library."""
    try:
        with open(config_filepath) as fp:
            config = yaml.safe_load(fp)
    except FileNotFoundError:
        config = None

    if config is None:
        config = {}
    elif not isinstance(config, dict):
        raise RuntimeError(
            f'ERROR: zoia configuration file {config_filepath} is not a '
            f'dictionary. Got data of type {type(config)} instead.'
        )

    config['directory'] = library_root

    with open(config_filepath, 'w') as fp:
        yaml.safe_dump(config, fp)

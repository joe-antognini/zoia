"""Edit the `zoia` configuration file."""

import click

import zoia.backend.config
import zoia.parse.yaml


def _config_validator(obj):
    try:
        zoia.backend.config.ZoiaConfig(**obj)
    except Exception as e:
        raise zoia.parse.yaml.ZoiaYamlValidationError(str(e))


@click.command()
def config():
    """Edit `zoia`'s configuration file."""
    config_filename = zoia.backend.config.get_config_filepath()
    with open(config_filename) as fp:
        config_text = fp.read()

    new_config = zoia.parse.yaml.edit_until_valid(
        config_text, validation_fn=_config_validator
    )

    new_config_str = zoia.parse.yaml.dump(new_config)
    with open(config_filename, 'w') as fp:
        fp.write(new_config_str)

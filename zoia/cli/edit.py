"""Edit the metadata for a document."""

import json
import sys

import click

import zoia.backend.metadata
from zoia.backend.metadata import Metadatum
from zoia.parse import yaml as zoia_yaml


@click.command()
@click.option(
    '--syntax',
    type=click.Choice(['json', 'yaml'], case_sensitive=False),
    default='json',
    help='Which syntax to use to edit the metadata.',
)
@click.argument('citekey', required=True)
def edit(citekey, syntax):
    """Edit the metadata for a document."""
    try:
        metadatum = zoia.backend.metadata.get_metadata(citekey)
    except KeyError:
        click.secho(f'Citekey {citekey} does not exist in library.', fg='red')
        sys.exit(1)

    text = None
    extension = None
    if syntax == 'json':
        text = json.dumps(metadatum, indent=4)
        extension = '.json'
    elif syntax == 'yaml':
        text = zoia_yaml.dump(metadatum, indent=4)
        extension = '.yaml'
    else:
        click.secho(f'Got unsupported syntax {syntax}.', fg='red')
        sys.exit(1)

    new_metadatum_str = click.edit(text=text, extension=extension)
    if new_metadatum_str is not None:
        if syntax == 'json':
            try:
                new_metadatum = json.loads(new_metadatum_str)
            except json.JSONDecodeError:
                # TODO: Add a better error message here and give the user the
                # opportunity to fix the mistake.
                click.secho(
                    'Could not parse JSON, didn\'t save metadata.', fg='red'
                )
                sys.exit(1)
        elif syntax == 'yaml':
            new_metadatum = zoia_yaml.edit_until_valid(new_metadatum_str)
            if new_metadatum is None:
                click.secho('Didn\'t save metadata.', fg='red')
                sys.exit(1)
    else:
        click.secho('File not saved, not changing metadata.', fg='red')
        sys.exit(1)

    zoia.backend.metadata.replace_metadata(citekey, new_metadatum)

    click.secho(
        f'Successfully edited metadata for '
        f'{str(Metadatum.from_dict(new_metadatum))}.',
        fg='blue',
    )

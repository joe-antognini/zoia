"""Edit the metadata for a document."""

import json
import sys

import click
import yaml

import zoia.config
from zoia.metadata import Metadatum


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
    metadata = zoia.metadata.load_metadata()
    if citekey not in metadata:
        click.secho(f'Citekey {citekey} does not exist in library.', fg='red')
        sys.exit(1)

    metadatum = metadata[citekey]
    text = None
    extension = None
    if syntax == 'json':
        text = json.dumps(metadatum, indent=4)
        extension = '.json'
    elif syntax == 'yaml':
        text = yaml.dump(metadatum, indent=4)
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
            try:
                new_metadatum = yaml.safe_load(new_metadatum_str)
            except yaml.parser.ParserError:
                # TODO: Add a better error message here and give the user the
                # opportunity to fix the mistake.
                click.secho(
                    'Could not parse YAML, failed to save metadata.', fg='red'
                )
                sys.exit(1)
    else:
        click.secho('File not saved, not changing metadata.', fg='red')
        sys.exit(1)

    zoia.metadata.replace_metadata(citekey, new_metadatum)

    click.secho(
        f'Successfully edited metadata for '
        f'{str(Metadatum.from_dict(new_metadatum))}.',
        fg='blue',
    )

"""Add new documents to the library."""

import sys

import click

import zoia.backend.add
from zoia.backend.add import ZoiaAddException


@click.command()
@click.argument('identifier', required=True)
@click.option(
    '--citekey',
    type=str,
    default=None,
    help='Specify the BibTex citation key.',
)
def add(identifier, citekey):
    config = zoia.backend.config.load_config()

    try:
        citekey, metadatum, info_messages = zoia.backend.add.add(
            config, identifier, citekey
        )
        for message in info_messages:
            click.secho(message)
    except ZoiaAddException as e:
        click.secho(str(e), fg='red')
        sys.exit(1)

    click.secho(f'Success! Added {citekey}:', fg='blue')
    click.secho(f'    {str(metadatum)}', fg='blue')

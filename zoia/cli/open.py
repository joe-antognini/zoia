"""Open a document in the library."""

import os
import sys

import click

import zoia.backend.config


def _open(citekey):
    config = zoia.backend.config.load_config()
    document_path = os.path.join(config.library_root, citekey, 'document.pdf')
    if not os.path.isfile(document_path):
        raise FileNotFoundError(f'No document found for citekey {citekey}.')

    click.launch(document_path)


@click.command(name='open')
@click.argument('citekey', required=True)
def open_(citekey):
    """Open a document in the library."""
    try:
        _open(citekey)
    except FileNotFoundError as e:
        click.secho(str(e), fg='red')
        sys.exit(1)

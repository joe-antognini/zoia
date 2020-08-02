"""Implementation of the `zoia init` command."""

import os
import sys

import click

import zoia
from zoia.config import get_library_root
from zoia.config import set_library_root
from zoia.config import ZOIA_CONFIG_ROOT


@click.command()
@click.argument('directory', required=False, default=None)
def init(directory):
    """Initialize the `zoia` library."""
    if directory is None:
        if len(os.listdir()) == 0:
            default_directory = os.getcwd()
        else:
            default_directory = os.path.join(os.getcwd(), 'zoia')
        directory = click.prompt(
            'Provide a directory for your library',
            default=default_directory,
        )
        if directory is None:
            directory = default_directory

    if len(os.listdir(directory)) != 0:
        click.secho('ERROR: Directory provided must be empty. Exiting.')
        sys.exit(1)

    os.makedirs(ZOIA_CONFIG_ROOT, exist_ok=True)
    existing_library_root = get_library_root()
    if existing_library_root is not None:
        confirmation = click.confirm(
            f'WARNING: Found existing library at {existing_library_root}. '
            f'Use new directory?'
        )
        if not confirmation:
            click.secho('Aborting init.')
            sys.exit(1)
    set_library_root(directory)

    # Start with an empty dictionary in the metadata file.
    zoia.metadata.write_metadata({})

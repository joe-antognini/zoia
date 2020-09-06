"""Implementation of the `zoia init` command."""

import os
import sys
from pathlib import Path

import click

import zoia
import zoia.metadata
from zoia.config import get_library_root
from zoia.config import set_library_root


def _is_valid_init_dir(directory):
    """Determine whether a given directory is a valid root directory for zoia.

    A valid directory must either not exist or be empty.

    """
    if directory is None:
        return False

    return not Path(directory).exists() or len(os.listdir(directory)) == 0


def _get_default_directory():
    """Return a default directory for the zoia library root.

    The default library root will be set by trying the following directories in
    order until a valid directory is found:

    1. The user's current working directory.
    2. A subdirectory of the user's current working directory called `zoia`.

    If no valid directory is found from that list no default will be provided.

    """
    default_directories = [os.getcwd(), os.path.join(os.getcwd(), 'zoia')]
    for default_directory in default_directories:
        if _is_valid_init_dir(default_directory):
            return default_directory

    return None


@click.command()
@click.argument('directory', required=False, default=None)
def init(directory):
    """Initialize the `zoia` library."""
    current_library_root = get_library_root()
    if current_library_root is not None:
        click.secho(
            f'Warning: Found existing zoia library at {current_library_root}',
            fg='yellow',
        )
        confirmation = click.confirm('Choose a new directory?')
        if not confirmation:
            click.secho('Exiting.', fg='red')
            sys.exit(1)

    while not _is_valid_init_dir(directory):
        if directory is not None:
            click.secho(
                f'Error: Directory {directory} exists and is not empty.',
                fg='red',
            )
        directory = click.prompt(
            'Please provide a directory for your library',
            default=_get_default_directory(),
        )
        directory = os.path.expanduser(directory)

    os.makedirs(directory, exist_ok=True)
    set_library_root(directory)

    # Start with an empty dictionary in the metadata file.
    zoia.metadata.initialize_metadata()

    click.secho(
        f'Your zoia library was successfully initialized at {directory}!',
        fg='blue'
    )

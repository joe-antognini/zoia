"""Implementation of the `zoia init` command."""

import os
from pathlib import Path

import click

import zoia
import zoia.backend.metadata


def _is_valid_init_dir(directory):
    """Determine whether a given directory is a valid root directory for zoia.

    A valid directory must either not exist or be empty.

    """
    if directory is None:
        return False

    return not Path(directory).exists() or len(os.listdir(directory)) == 0


def _get_default_library_root():
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
def init():
    """Initialize the `zoia` library."""

    while True:
        library_root = click.prompt(
            'Please provide a directory for your library',
            default=_get_default_library_root(),
        )
        library_root = os.path.expanduser(library_root)

        if _is_valid_init_dir(library_root):
            break

        if library_root is not None:
            click.secho(
                f'Error: Directory {library_root} exists and is not empty.',
                fg='red',
            )

    os.makedirs(library_root, exist_ok=True)
    config = zoia.backend.config.ZoiaConfig(library_root=library_root)
    zoia.backend.config.save_config(config)

    os.makedirs(config.db_root, exist_ok=True)

    # Start with an empty dictionary in the metadata file.
    metadata = zoia.backend.metadata.get_metadata(config)
    metadata.write()

    click.secho(
        f'Your zoia library was successfully initialized at {library_root}!',
        fg='blue',
    )

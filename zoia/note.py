"""Write a note for a paper."""

import os
import sys

import click

import zoia.config


@click.command()
@click.argument('citekey', required=True)
def note(citekey):
    """Write a note for a document."""
    metadata = zoia.metadata.load_metadata()
    if citekey not in metadata:
        click.secho(f'Citekey {citekey} does not exist in library.', fg='red')
        sys.exit(1)

    note_path = os.path.join(
        zoia.config.get_library_root(), citekey, 'notes.md'
    )

    if not os.path.isfile(note_path):
        # TODO: Add a header here.
        pass

    click.edit(filename=note_path)

"""Write a note for a paper."""

import os
import sys

import click

import zoia.config
import zoia.yaml


def _create_header(metadatum):
    """Create a header string for a paper."""
    header = {}
    if 'title' in metadatum:
        header['title'] = metadatum['title']
    if 'authors' in metadatum:
        authors = metadatum['authors']
        if len(authors) <= 4:
            header['authors'] = [' '.join(author) for author in authors]
        else:
            header['authors'] = [' '.join(author) for author in authors[:3]]
            header['authors'].append('et al.')
    if 'year' in metadatum:
        header['year'] = metadatum['year']
    if 'tags' in metadatum:
        header['tags'] = ', '.join(metadatum['tags'])

    return '---\n' + zoia.yaml.dump(header, indent=4) + '---\n'


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

    text = None
    if not os.path.isfile(note_path):
        text = _create_header(metadata[citekey])

    click.edit(text=text, filename=note_path)

"""Write a note for a paper."""

import os
import sys
import yaml

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

    header = _create_header(metadata[citekey])
    body = ''
    if os.path.isfile(note_path):
        with open(note_path) as fp:
            body = fp.read()

    text = header + body
    while True:
        text = click.edit(text=text, extension='.md')

        if text is not None:
            try:
                note_docs = yaml.safe_load_all(text)
                header = next(note_docs)
                body = zoia.yaml.remove_header(text)
                with open(note_path, 'w') as fp:
                    fp.write(body)
            except StopIteration:
                # We reach here if the user provided only one document.  (Maybe
                # they deleted the header.)  Save the whole thing.
                with open(note_path, 'w') as fp:
                    fp.write(text)
            except (yaml.scanner.ScannerError, yaml.parser.ParserError):
                if click.confirm(
                    'Error parsing header. Continue editing? If no, the file'
                    'will be saved as is.'
                ):
                    continue
                else:
                    with open(note_path, 'w') as fp:
                        fp.write(text)
        else:
            click.secho('No input recorded. Nothing saved.', fg='red')

        break

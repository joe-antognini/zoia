"""Add tags to entries."""

import sys

import click

import zoia.backend.metadata


@click.command()
@click.argument('citekey', required=True)
@click.argument('tags', nargs=-1)
def tag(citekey, tags):
    """Add tags to an entry."""

    config = zoia.backend.config.load_config()
    metadata = zoia.backend.metadata.get_metadata(config)

    if citekey not in metadata:
        click.secho(
            f'Citekey {citekey} does not exist in the library.', fg='red'
        )
        sys.exit(1)

    metadatum = metadata[citekey]

    if 'tags' not in metadatum:
        metadatum['tags'] = tags[:]
    else:
        metadatum['tags'].extend(
            [elem for elem in tags if elem not in metadatum['tags']]
        )

    metadata.replace(citekey, metadatum)

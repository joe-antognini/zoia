"""Add new documents to the library."""

import sys
from enum import Enum

import click

import zoia.ids.arxiv


class IdType(Enum):
    DOI = 'doi'
    ARXIV = 'arxiv'
    ISBN = 'isbn'


def _add_arxiv_id(identifier):
    # TODO
    pass


@click.command()
@click.argument('identifier', required=True)
@click.option('--citekey', type=str, help='Specify the BibTex citation key.')
def add(identifier, citekey):
    is_arxiv = zoia.arxiv.is_valid_arxiv_id(identifier)
    if not is_arxiv and identifier.lower().startswith('arxiv:'):
        click.secho(
            'It looks like you\'re trying to provide an arXiv ID, but the ID '
            'is malformed.',
            fg='red',
        )
        sys.exit(1)

    if is_arxiv:
        _add_arxiv_id(identifier)

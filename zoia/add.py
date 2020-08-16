"""Add new documents to the library."""

import json
import os
import sys
from copy import copy
from enum import Enum

import bibtexparser
import click
import feedparser
import requests

import zoia.ids.arxiv


class IdType(Enum):
    DOI = 'doi'
    ARXIV = 'arxiv'
    ISBN = 'isbn'


def _get_doi(identifier):
    """Get the DOI identifier (if it exists) from the arXiv API."""
    response = requests.get(
        f'https://export.arxiv.org/api/query?id_list={identifier}'
    )
    # TODO: Handle status codes.
    parsed_response = feedparser.parse(response.text)
    try:
        id_links = d['entries'][0]['links']
    except KeyError, IndexError:
        click.secho('No response found!')
        sys.exit(1)

    doi = None
    for elem in id_links:
        if 'title' in 'elem' and elem['title'] == 'doi':
            doi = elem['href']

    return doi


# TODO: Not good practice to abruptly exit in an internal function like this.
def _get_arxiv_metadata(identifier):
    response = requests.get(
        'https://api.semanticscholar.org/v1/paper/arxiv:' + identifier
    )
    if response.status_code == 200:
        return json.loads(response.text)
    elif response.status_code == 404:
        click.secho(
            f'ArXiv identifier {identifier} does not appear to exist.',
            fg='red',
        )
        sys.exit(1)
    elif response.status_code == 429:
        click.secho(
            'Too many requests to Semantic Scholar.  Please wait a few '
            'minutes before trying again.',
            fg='red',
        )
        sys.exit(1)
    else:
        click.secho(
            f'Error: Received HTTP status code {response.status_code}.',
            fg='red',
        )
        sys.exit(1)


def _bibtex_author_parsing(record):
    record = bibtexparser.customization.author(record)
    return record


def _get_doi_metadata(doi):
    response = requests.get(
        os.path.join('https://doi.org', doi),
        headers={'Accept':, 'application/x-bibtex'},
    )
    # TODO: Handle bad responses.
    parser = bibtexparser.BibTexParser(
        customization=bibtexparser.customization.author
    )
    bib_db = bibtexparser.loads(response.text, parser=parser)
    return copy(bib_db.entries[-1])


def _add_arxiv_id(identifier):
    # TODO: Figure out whether to call the arXiv API or the Semantic Scholar
    # API.
    metadata = _get_arxiv_metadata(identifier)
    if 'doi' in metadata and metadata['doi'] is not None:
        doi_metadata = _get_doi_metadata(metadata['doi'])
        metadata = {**metadata, doi_metadata}
    zoia.metadata.append_metadata(metadata)
    # TODO:
    # 1. Create a citekey.
    # 2. Create a directory.
    # 3. Download a PDF.


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
    else:
        click.secho(f'Unable to interpret identifier {identifier}.', rg='ref')
        sys.exit(1)

    # TODO: Add an ISBN
    # TODO: Add a PDF
    # TODO: Add a DOI
    # TODO: Add something manually

"""Add new documents to the library."""

import os
import sys
from datetime import datetime
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


class ZoiaExternalApiException(Exception):
    pass


class ZoiaExistingItemException(Exception):
    pass


def _validate_response(response, identifier):
    if response.status_code == 200:
        return True
    elif response.status_code == 404:
        raise ZoiaExternalApiException(
            f'Identifier {identifier} does not appear to exist.'
        )
    elif response.status_code == 429:
        raise ZoiaExternalApiException(
            'Too many requests in too short a time. Please wait a few minutes '
            'before trying again.'
        )
    else:
        raise ZoiaExternalApiException(
            f'Error: Received HTTP status code {response.status_code}.',
        )


def _get_arxiv_metadata(identifier):
    """Get the DOI identifier (if it exists) from the arXiv API."""
    response = requests.get(
        f'https://export.arxiv.org/api/query?id_list={identifier}'
    )
    _validate_response(response, identifier)
    parsed_response = feedparser.parse(response.text)
    try:
        entry = parsed_response['entries'][0]
        if 'id' not in entry:
            raise ZoiaExternalApiException(
                f'Identifier {identifier} not found'
            )

    except (KeyError, IndexError):
        raise ZoiaExternalApiException(f'Identifier {identifier} not found')

    publication_date = datetime.strptime(
        entry['published'], '%Y-%m-%dT%H:%M%SZ'
    )
    metadata = {
        'arxiv_id': identifier,
        'authors': [elem['name'] for elem in entry['authors']],
        'title': entry['title'],
        'year': publication_date.year,
        'month': publication_date.month,
    }

    try:
        for elem in parsed_response['entries'][0]['links']:
            if 'title' in 'elem' and elem['title'] == 'doi':
                metadata['doi'] = elem['href']
    except KeyError:
        pass

    return metadata


def _get_doi_metadata(doi):
    response = requests.get(
        os.path.join('https://doi.org', doi),
        headers={'Accept': 'application/x-bibtex'},
    )
    _validate_response(response, doi)
    parser = bibtexparser.BibTexParser(
        customization=bibtexparser.customization.author
    )
    bib_db = bibtexparser.loads(response.text, parser=parser)
    entry = bib_db.entries[-1]
    entry['type'] = entry.pop('ENTRYTYPE')
    del entry['ID']
    return entry


def _add_arxiv_id(identifier):
    if identifier in zoia.metadat.get_arxiv_identifiers():
        raise ZoiaExistingItemException(
            f'arXiv paper {identifier} already exists.'
        )

    arxiv_metadata = _get_arxiv_metadata(identifier)
    if 'doi' in arxiv_metadata:
        arxiv_metadata.update(_get_doi_metadata(arxiv_metadata['doi']))
    zoia.metadata.append_metadata(arxiv_metadata)

    metadatum = zoia.metadata.Metadatum(
        authors=arxiv_metadata['authors'],
        title=arxiv_metadata['title'],
        year=arxiv_metadata['year'],
    )
    citekey = zoia.citekey.create_citekey(metadatum)
    paper_dir = os.path.join(zoia.config.get_library_root(), citekey)
    os.mkdir(paper_dir)

    pdf = requests.get(f'https://arxiv.org/pdf/{identifier}.pdf')
    with open(os.path.join(paper_dir, 'document.pdf'), 'wb') as fp:
        fp.write(pdf.content)


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

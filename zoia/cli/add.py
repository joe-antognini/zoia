"""Add new documents to the library."""

import hashlib
import json
import os
import shutil
import sys
from datetime import datetime
from multiprocessing.dummy import Process as ThreadProcess
from multiprocessing.dummy import Queue as ThreadQueue
from textwrap import dedent

import bibtexparser
import click
import feedparser
import isbnlib
import requests
from halo import Halo

import zoia.backend.config
import zoia.backend.metadata
import zoia.parse.citekey
import zoia.parse.pdf
from zoia.parse.classification import classify_and_normalize_identifier
from zoia.parse.classification import IdType
from zoia.parse.classification import ZoiaUnknownIdentifierException
from zoia.parse.normalization import split_name


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
        entry['published'], '%Y-%m-%dT%H:%M:%SZ'
    )
    metadata = {
        'arxiv_id': identifier,
        'authors': [split_name(elem['name']) for elem in entry['authors']],
        'title': entry['title'].replace('\n ', ''),
        'year': publication_date.year,
        'month': publication_date.month,
    }

    if 'arxiv_doi' in entry:
        metadata['doi'] = entry['arxiv_doi']

    return metadata


def _get_doi_metadata(doi):
    response = requests.get(
        os.path.join('https://doi.org', doi),
        headers={'Accept': 'application/x-bibtex'},
    )
    _validate_response(response, doi)
    parser = bibtexparser.bparser.BibTexParser(
        customization=bibtexparser.customization.author
    )
    bib_db = bibtexparser.loads(response.text, parser=parser)
    entry = bib_db.entries[-1]
    if 'type' in entry:
        entry['type'] = entry.pop('ENTRYTYPE')

    if 'year' in entry:
        entry['year'] = int(entry['year'])

    entry['authors'] = entry.pop('author')
    entry['authors'] = [
        list(map(lambda x: x.strip(), reversed(elem.split(','))))
        for elem in entry['authors']
    ]

    del entry['ID']
    return entry


def _get_isbn_metadata(isbn):
    metadata = isbnlib.meta(isbn, service='goob')
    if not {'Authors', 'Title', 'Year'}.issubset(set(metadata)):
        raise ZoiaExternalApiException(
            f'Did not receive authors, title, or year for ISBN {isbn}.'
        )

    metadata['isbn'] = metadata.pop('ISBN-13')
    keys = list(metadata.keys())
    for key in keys:
        metadata[key.lower()] = metadata.pop(key)

    metadata['authors'] = list(map(split_name, metadata['authors']))

    try:
        metadata['year'] = int(metadata['year'])
    except ValueError:
        raise ZoiaExternalApiException(
            'Google Books returned a value "{}" for the year that could '
            'not be converted to an integer.'.format(metadata['year'])
        )

    return metadata


def _add_arxiv_id(identifier, citekey=None):
    if identifier in zoia.backend.metadata.get_arxiv_ids():
        raise ZoiaExistingItemException(
            f'arXiv paper {identifier} already exists.'
        )

    # Downloading the PDF can take a while, so start it early in a separate
    # thread.
    pdf_queue = ThreadQueue()
    pdf_process = ThreadProcess(
        target=lambda q, x: q.put(requests.get(x)),
        args=(pdf_queue, f'https://arxiv.org/pdf/{identifier}.pdf'),
    )
    pdf_process.start()

    with Halo(text='Querying arXiv...', spinner='dots'):
        arxiv_metadata = _get_arxiv_metadata(identifier)

    if 'doi' in arxiv_metadata:
        with Halo(text='Querying DOI information...', spinner='dots'):
            arxiv_metadata.update(_get_doi_metadata(arxiv_metadata['doi']))

    if citekey is None:
        metadatum = zoia.backend.metadata.Metadatum(
            authors=arxiv_metadata['authors'],
            title=arxiv_metadata['title'],
            year=arxiv_metadata['year'],
        )
        citekey = zoia.parse.citekey.create_citekey(metadatum)
    paper_dir = os.path.join(zoia.backend.config.get_library_root(), citekey)
    os.mkdir(paper_dir)

    with Halo(text='Downloading PDF...', spinner='dots'):
        pdf = pdf_queue.get()
        pdf_process.join()

    if pdf.status_code == 200:
        with open(os.path.join(paper_dir, 'document.pdf'), 'wb') as fp:
            fp.write(pdf.content)
        arxiv_metadata['pdf_md5'] = hashlib.md5(pdf.content).hexdigest()
    else:
        click.secho('Was unable to fetch a PDF', fg='yellow')

    zoia.backend.metadata.append_metadata(citekey, arxiv_metadata)

    return metadatum


def _add_isbn(identifier, citekey):
    """Add an entry from an ISBN."""
    if identifier in zoia.backend.metadata.get_isbns():
        raise ZoiaExistingItemException(f'ISBN {identifier} already exists.')

    with Halo(text='Querying ISBN metadata...', spinner='dots'):
        isbn_metadata = _get_isbn_metadata(identifier)

    if citekey is None:
        metadatum = zoia.backend.metadata.Metadatum(
            authors=isbn_metadata['authors'],
            title=isbn_metadata['title'],
            year=isbn_metadata['year'],
        )
        citekey = zoia.parse.citekey.create_citekey(metadatum)

    zoia.backend.metadata.append_metadata(citekey, isbn_metadata)

    book_dir = os.path.join(zoia.backend.config.get_library_root(), citekey)
    os.mkdir(book_dir)

    return metadatum


def _add_doi(identifier, citekey):
    """Add an entry from a DOI."""
    if identifier in zoia.backend.metadata.get_dois():
        raise ZoiaExistingItemException(f'DOI {identifier} already exists.')

    # Query Semantic Scholar to get the corresponding arxiv ID (if there is
    # one) in a separate thread.
    arxiv_queue = ThreadQueue()
    arxiv_process = ThreadProcess(
        target=lambda q, x: q.put(requests.get(x)),
        args=(
            arxiv_queue,
            f'https://api.semanticscholar.org/v1/paper/{identifier}',
        ),
    )
    arxiv_process.start()

    with Halo(text='Querying DOI metadata...'):
        doi_metadata = _get_doi_metadata(identifier)

    metadatum = zoia.backend.metadata.Metadatum(
        authors=doi_metadata['authors'],
        title=doi_metadata['title'],
        year=doi_metadata['year'],
    )

    if citekey is None:
        citekey = zoia.parse.citekey.create_citekey(metadatum)

    paper_dir = os.path.join(zoia.backend.config.get_library_root(), citekey)
    os.mkdir(paper_dir)

    with Halo(text='Querying Semantic Scholar for corresponding arXiv ID...'):
        arxiv_metadata_response = arxiv_queue.get()
        arxiv_process.join()

    arxiv_metadata = json.loads(arxiv_metadata_response.text)

    if (arxiv_id := arxiv_metadata.get('arxivId')) is not None:
        doi_metadata['arxiv_id'] = arxiv_id
        with Halo(text='Downloading PDF from arXiv...'):
            pdf_response = requests.get(
                f'https://arxiv.org/pdf/{arxiv_id}.pdf'
            )

        if pdf_response.status_code == 200:
            with open(os.path.join(paper_dir, 'document.pdf'), 'wb') as fp:
                fp.write(pdf_response.content)
            doi_metadata['pdf_md5'] = hashlib.md5(
                pdf_response.content
            ).hexdigest()
        else:
            click.secho('Was unable to fetch a PDF', fg='yellow')

    zoia.backend.metadata.append_metadata(citekey, doi_metadata)

    return metadatum


def _add_pdf(identifier, citekey, move_paper=False):
    """Add a PDF file."""
    md5_hashes = zoia.backend.metadata.get_md5_hashes()
    with open(identifier, 'rb') as fp:
        pdf = fp.read()
    md5_hash = hashlib.md5(pdf).hexdigest()
    if md5_hash in md5_hashes:
        raise ZoiaExistingItemException(f'PDF{identifier} already exists.')

    doi = zoia.parse.pdf.get_doi_from_pdf(identifier)
    if doi is not None:
        with Halo(text='Found DOI, querying metadata...'):
            metadata = _get_doi_metadata(doi)

        metadatum = zoia.backend.metadata.Metadatum.from_dict(metadata)
        click.secho(f'Found DOI for {str(metadatum)}')
        if not click.confirm('Does this look correct?'):
            text = dedent(
                '''\
                # Please fill out the document's metadata in YAML format.  You
                # can add additional fields, but the fields in the template
                # must be filled out.
                title:
                authors:
                    -
                year:
                '''
            )
            metadata = zoia.yaml.edit_until_valid(
                text, validator_fn=zoia.yaml.metadata_validator
            )
            if metadata is None:
                click.secho('Couldn\'t parse metadata, not adding PDF.')
                sys.exit(1)

            metadatum = zoia.backend.metadata.Metadatum.from_dict(metadata)
    else:
        text = dedent(
            '''\
            # No DOI was found for the PDF.  Please fill out the document's
            # metadata in YAML format.  You can add additional fields, but
            # the fields in the template must be filled out.
            title:
            authors:
                -
            year:
            '''
        )

        metadata = zoia.yaml.edit_until_valid(
            text, validator_fn=zoia.yaml.metadata_validator
        )

        if metadata is None:
            click.secho('Couldn\'t parse metadata, not adding PDF.')
            sys.exit(1)

        metadatum = zoia.backend.metadata.Metadatum.from_dict(metadata)

    if citekey is None:
        citekey = zoia.parse.citekey.create_citekey(metadatum)

    paper_dir = os.path.join(zoia.backend.config.get_library_root(), citekey)
    os.mkdir(paper_dir)
    if move_paper:
        shutil.move(identifier, os.path.join(paper_dir, 'document.pdf'))
    else:
        shutil.copyfile(identifier, os.path.join(paper_dir, 'document.pdf'))

    metadata['pdf_md5'] = md5_hash
    zoia.backend.metadata.append_metadata(citekey, metadata)

    return metadatum


@click.command()
@click.argument('identifier', required=True)
@click.option(
    '--citekey',
    type=str,
    default=None,
    help='Specify the BibTex citation key.',
)
def add(identifier, citekey):
    if (
        citekey is not None
        and citekey in zoia.backend.metadata.load_metadata()
    ):
        click.secho(f'Citekey {citekey} already exists.', fg='red')
        sys.exit(1)

    try:
        id_type, normalized_identifier = classify_and_normalize_identifier(
            identifier
        )
    except ZoiaUnknownIdentifierException:
        click.secho(
            f'Cannot determine what kind of identifier {identifier} is.',
            fg='red',
        )
        sys.exit(1)

    try:
        if id_type == IdType.ARXIV:
            metadatum = _add_arxiv_id(normalized_identifier, citekey)
        elif id_type == IdType.ISBN:
            metadatum = _add_isbn(normalized_identifier, citekey)
        elif id_type == IdType.DOI:
            metadatum = _add_doi(normalized_identifier, citekey)
        elif id_type == IdType.PDF:
            metadatum = _add_pdf(normalized_identifier, citekey)
    except (ZoiaExternalApiException, ZoiaExistingItemException) as e:
        click.secho(f'{str(e)}', fg='red')
        sys.exit(1)

    # TODO: Add something manually

    click.secho(f'Success! Added {str(metadatum)}.', fg='blue')

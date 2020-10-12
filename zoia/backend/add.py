"""Module to add an item to the library."""

import hashlib
import json
import os
import shutil
from multiprocessing.dummy import Process as ThreadProcess
from multiprocessing.dummy import Queue as ThreadQueue
from textwrap import dedent

import bibtexparser
import click
import isbnlib
import requests

import zoia.backend.config
import zoia.backend.metadata
import zoia.parse.citekey
import zoia.parse.pdf
from zoia.backend.status import StatusMessage
from zoia.parse.classification import classify_and_normalize_identifier
from zoia.parse.classification import IdType
from zoia.parse.classification import ZoiaUnknownIdentifierException
from zoia.parse.normalization import split_name


class ZoiaAddException(Exception):
    """A generic exception for errors encountered when adding new items."""


def _validate_response(response, identifier):
    if response.status_code == 200:
        return True
    elif response.status_code == 404:
        raise ZoiaAddException(
            f'Identifier {identifier} does not appear to exist.'
        )
    elif response.status_code == 429:
        raise ZoiaAddException(
            'Too many requests in too short a time. Please wait a few minutes '
            'before trying again.'
        )
    else:
        raise ZoiaAddException(
            f'Error: Received HTTP status code {response.status_code}.',
        )


def _get_arxiv_metadata(identifier):
    """Get the DOI identifier (if it exists) from the arXiv API."""
    response = requests.get(
        f'https://api.semanticscholar.org/v1/paper/arXiv:{identifier}'
    )
    _validate_response(response, identifier)
    parsed_response = json.loads(response.text)

    if 'title' not in parsed_response:
        raise RuntimeError('Received response that didn\'t include a title.')
    if 'authors' not in parsed_response:
        raise RuntimeError(
            'Received response that didn\'t include an authors list.'
        )
    if 'year' not in parsed_response:
        raise RuntimeError('Received response that didn\'t include a year.')

    title = parsed_response['title']
    authors = [split_name(elem['name']) for elem in parsed_response['authors']]
    year = parsed_response['year']

    metadata = {
        'arxiv_id': identifier,
        'entry_type': 'article',
        'title': title,
        'authors': authors,
        'year': year,
        'url': f'https://arxiv.org/abs/{identifier}',
    }

    if parsed_response.get('doi') is not None:
        metadata['doi'] = parsed_response['doi']

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
    if 'ENTRYTYPE' in entry:
        entry['entry_type'] = entry.pop('ENTRYTYPE')
    else:
        entry['entry_type'] = 'article'

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
        raise ZoiaAddException(
            f'Did not receive authors, title, or year for ISBN {isbn}.'
        )

    metadata['entry_type'] = 'book'
    metadata['isbn'] = metadata.pop('ISBN-13')
    keys = list(metadata.keys())
    for key in keys:
        metadata[key.lower()] = metadata.pop(key)

    metadata['authors'] = list(map(split_name, metadata['authors']))

    try:
        metadata['year'] = int(metadata['year'])
    except ValueError:
        raise ZoiaAddException(
            'Google Books returned a value "{}" for the year that could '
            'not be converted to an integer.'.format(metadata['year'])
        )

    return metadata


def _add_arxiv_id(metadata, identifier, citekey=None):
    info_messages = []
    with StatusMessage('Querying arXiv...') as message:
        if metadata.arxiv_id_exists(identifier):
            raise ZoiaAddException(f'arXiv paper {identifier} already exists.')

        # Downloading the PDF can take a while, so start it early in a separate
        # thread.
        pdf_queue = ThreadQueue()
        pdf_process = ThreadProcess(
            target=lambda q, x: q.put(requests.get(x)),
            args=(pdf_queue, f'https://arxiv.org/pdf/{identifier}.pdf'),
        )
        pdf_process.start()

        arxiv_metadata = _get_arxiv_metadata(identifier)

        if 'doi' in arxiv_metadata:
            message.update('Querying DOI information...')
            arxiv_metadata.update(_get_doi_metadata(arxiv_metadata['doi']))

        if citekey is None:
            metadatum = zoia.backend.metadata.Metadatum.from_dict(
                arxiv_metadata
            )
            citekey = zoia.parse.citekey.create_citekey(metadata, metadatum)
        paper_dir = os.path.join(metadata.config.library_root, citekey)
        os.mkdir(paper_dir)

        message.update(text='Downloading PDF...')
        pdf = pdf_queue.get()
        pdf_process.join()

        if pdf.status_code == 200:
            with open(os.path.join(paper_dir, 'document.pdf'), 'wb') as fp:
                fp.write(pdf.content)
            md5_hash = hashlib.md5(pdf.content).hexdigest()
            arxiv_metadata['pdf_md5'] = md5_hash
            if metadata.pdf_md5_hash_exists(md5_hash):
                raise ZoiaAddException(
                    f'arXiv paper {identifier} already exists.'
                )
        else:
            info_messages.append('Was unable to fetch a PDF')

        metadata[citekey] = arxiv_metadata

    return citekey, metadatum, info_messages


def _add_isbn(metadata, identifier, citekey):
    """Add an entry from an ISBN."""
    info_messages = []
    with StatusMessage('Querying ISBN metadata...'):
        if metadata.isbn_exists(identifier):
            raise ZoiaAddException(f'ISBN {identifier} already exists.')

        isbn_metadata = _get_isbn_metadata(identifier)

        if citekey is None:
            metadatum = zoia.backend.metadata.Metadatum.from_dict(
                isbn_metadata
            )
            citekey = zoia.parse.citekey.create_citekey(metadata, metadatum)

        metadata[citekey] = isbn_metadata

        book_dir = os.path.join(metadata.config.library_root, citekey)
        os.mkdir(book_dir)

    return citekey, metadatum, info_messages


def _add_doi(metadata, identifier, citekey):
    """Add an entry from a DOI."""
    info_messages = []
    with StatusMessage('Querying DOI metadata...') as message:
        if metadata.doi_exists(identifier):
            raise ZoiaAddException(f'DOI {identifier} already exists.')

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

        doi_metadata = _get_doi_metadata(identifier)

        metadatum = zoia.backend.metadata.Metadatum.from_dict(doi_metadata)

        if citekey is None:
            citekey = zoia.parse.citekey.create_citekey(metadata, metadatum)

        paper_dir = os.path.join(metadata.config.library_root, citekey)
        os.mkdir(paper_dir)

        message.update(
            'Querying Semantic Scholar for corresponding arXiv ID...'
        )
        arxiv_metadata_response = arxiv_queue.get()
        arxiv_process.join()

        arxiv_metadata = json.loads(arxiv_metadata_response.text)

        if (arxiv_id := arxiv_metadata.get('arxivId')) is not None:
            doi_metadata['arxiv_id'] = arxiv_id
            message.update('Downloading PDF from arXiv...')
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
                info_messages.append('Was unable to fetch a PDF')

        metadata[citekey] = doi_metadata

    return citekey, metadatum, info_messages


def _add_pdf(metadata, identifier, citekey, move_paper=False):
    """Add a PDF file."""
    info_messages = []
    with StatusMessage('Adding PDF...') as message:
        with open(identifier, 'rb') as fp:
            pdf = fp.read()
        md5_hash = hashlib.md5(pdf).hexdigest()
        if metadata.pdf_md5_hash_exists(md5_hash):
            raise ZoiaAddException(f'PDF{identifier} already exists.')

        doi = zoia.parse.pdf.get_doi_from_pdf(identifier)
        if doi is not None:
            if metadata.doi_exists(doi):
                raise ZoiaAddException(
                    f'DOI corresponding to {identifier} already exists.'
                )
            message.update(text='Found DOI, querying metadata...')
            doi_metadata = _get_doi_metadata(doi)

            metadatum = zoia.backend.metadata.Metadatum.from_dict(doi_metadata)
            click.secho(f'Found DOI {doi} for {str(metadatum)}')
            if not click.confirm('Does this look correct?'):
                text = dedent(
                    '''\
                    # Please fill out the document's metadata in YAML format.
                    # You can add additional fields, but the fields in the
                    # template must be filled out.
                    title:
                    authors:
                        -
                    year:
                    '''
                )
                metadatum_dict = zoia.yaml.edit_until_valid(
                    text, validator_fn=zoia.yaml.metadata_validator
                )
                if metadatum_dict is None:
                    raise ZoiaAddException(
                        "Couldn't parse metadata, not adding PDF."
                    )

                metadatum = zoia.backend.metadata.Metadatum.from_dict(
                    metadatum_dict
                )
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

            metadatum_dict = zoia.yaml.edit_until_valid(
                text, validator_fn=zoia.yaml.metadata_validator
            )

            if metadatum_dict is None:
                raise ZoiaAddException(
                    "Couldn't parse metadata, not adding PDF."
                )

            metadatum = zoia.backend.metadata.Metadatum.from_dict(
                metadatum_dict
            )

        if citekey is None:
            citekey = zoia.parse.citekey.create_citekey(metadata, metadatum)

        paper_dir = os.path.join(metadata.config.library_root, citekey)
        os.mkdir(paper_dir)
        if move_paper:
            shutil.move(identifier, os.path.join(paper_dir, 'document.pdf'))
        else:
            shutil.copyfile(
                identifier, os.path.join(paper_dir, 'document.pdf')
            )

        metadatum_dict = metadatum.to_dict()
        metadatum_dict['pdf_md5'] = md5_hash
        metadata[citekey] = metadatum_dict

    return citekey, metadatum, info_messages


def add(config, identifier, citekey=None):
    """Add a new document to the library."""

    metadata = zoia.backend.metadata.get_metadata(config)
    if citekey and citekey in metadata:
        raise ZoiaAddException(f'Citekey {citekey} already exists.')

    try:
        id_type, normalized_identifier = classify_and_normalize_identifier(
            identifier
        )
    except ZoiaUnknownIdentifierException:
        raise ZoiaAddException(
            f'Cannot determine what kind of identifier {identifier} is.',
        )

    if id_type == IdType.ARXIV:
        add_fn = _add_arxiv_id
    elif id_type == IdType.ISBN:
        add_fn = _add_isbn
    elif id_type == IdType.DOI:
        add_fn = _add_doi
    elif id_type == IdType.PDF:
        add_fn = _add_pdf
    return add_fn(metadata, normalized_identifier, citekey)

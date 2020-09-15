"""Module to classify identifiers."""

from enum import Enum

import zoia.ids


class IdType(Enum):
    DOI = 'doi'
    ARXIV = 'arxiv'
    ISBN = 'isbn'
    PDF = 'pdf'


class ZoiaUnknownIdentifierException(Exception):
    pass


def classify_and_normalize_identifier(identifier):
    """Classify an identifier and strip extraneous characters."""
    id_type = None
    if zoia.ids.pdf.is_pdf(identifier):
        id_type = IdType.PDF
    elif zoia.ids.arxiv.is_arxiv(identifier):
        id_type = IdType.ARXIV
        identifier = zoia.ids.arxiv.normalize(identifier)
    elif zoia.ids.isbn.is_isbn(identifier):
        id_type = IdType.ISBN
        identifier = zoia.ids.isbn.normalize(identifier)
    elif zoia.ids.doi.is_doi(identifier):
        id_type = IdType.DOI
        identifier = zoia.ids.doi.normalize(identifier)
    else:
        raise ZoiaUnknownIdentifierException(
            f'Cannot determine what kind of identifier is {identifier}.'
        )

    return id_type, identifier

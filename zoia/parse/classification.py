"""Module to classify identifiers."""

from enum import Enum

import zoia.parse.arxiv
import zoia.parse.doi
import zoia.parse.isbn
import zoia.parse.pdf


class IdType(Enum):
    DOI = 'doi'
    ARXIV = 'arxiv'
    ISBN = 'isbn'
    PDF = 'pdf'


class ZoiaUnknownIdentifierException(Exception):
    pass


def classify_identifier(identifier):
    """Classify an identifier."""
    id_type = None
    if zoia.parse.pdf.is_pdf(identifier):
        id_type = IdType.PDF
    elif zoia.parse.arxiv.is_arxiv(identifier):
        id_type = IdType.ARXIV
    elif zoia.parse.isbn.is_isbn(identifier):
        id_type = IdType.ISBN
    elif zoia.parse.doi.is_doi(identifier):
        id_type = IdType.DOI
    else:
        raise ZoiaUnknownIdentifierException(
            f'Cannot determine what kind of identifier is {identifier}.'
        )

    return id_type


def classify_and_normalize_identifier(identifier):
    """Classify an identifier and strip extraneous characters."""
    id_type = classify_identifier(identifier)

    if id_type == IdType.ARXIV:
        identifier = zoia.parse.arxiv.normalize(identifier)
    elif id_type == IdType.ISBN:
        identifier = zoia.parse.isbn.normalize(identifier)
    elif id_type == IdType.DOI:
        identifier = zoia.parse.doi.normalize(identifier)

    return id_type, identifier

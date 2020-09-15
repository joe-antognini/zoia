"""Functionality to handle ISBNs."""

import isbnlib


def _isbn_has_valid_checksum(identifier):
    """Determine whether the given ISBN has a valid checksum."""
    if len(identifier) == 10:
        identifier = '978' + identifier

    numerals = [int(char) for char in identifier]
    checksum = 0
    for i, numeral in enumerate(numerals):
        weight = 1 if i % 2 == 0 else 3
        checksum += weight * numeral

    return (checksum % 10) == 0


def is_isbn(identifier):
    """Determine whether the identifier could be an ISBN."""

    identifier = normalize(identifier)
    return isbnlib.is_isbn10(identifier) or isbnlib.is_isbn13(identifier)


def normalize(identifier):
    """Remove a possible prefix from the identifier."""

    identifier = identifier.lower()
    identifier = identifier.replace('-', '')
    prefix = 'isbn:'
    if identifier.startswith(prefix):
        identifier = identifier[len(prefix) :]

    if isbnlib.is_isbn10(identifier):
        identifier = isbnlib.to_isbn13(identifier)

    return identifier

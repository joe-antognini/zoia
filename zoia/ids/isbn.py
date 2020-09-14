"""Functionality to handle ISBNs."""


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

    identifier = identifier.replace('-', '')
    if identifier.isnumeric() and len(identifier) in {10, 13}:
        return _isbn_has_valid_checksum(identifier)

    return False

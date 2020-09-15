"""Functionality to interface with arXiv references."""

import re
import string

ARXIV_FIELDS = {
    'astro-ph',
    'cond-mat',
    'gr-qc',
    'hep-ex',
    'hep-lat',
    'hep-ph',
    'hep-th',
    'math-ph',
    'nlin',
    'nucl-ex',
    'physics',
    'quant-ph',
    'math',
    'cs',
    'q-bio',
    'q-fin',
    'stat',
    'eess',
    'econ',
}


# TODO: Handle versions!
def _is_valid_old_style_arxiv_id(identifier):
    """Determine if the given identifiier is a valid old style arXiv ID."""
    is_valid = True
    n_slashes = identifier.count('/')
    if n_slashes != 1:
        is_valid = False
    else:
        subject, identifier = identifier.split('/')
        # TODO: Check that the field and subject class are correctly formatted.
        if not identifier.isnumeric():
            is_valid = False
        # TODO: Check that the year is valid.
        elif int(identifier[2:4]) > 12 or int(identifier[2:4]) == 0:
            is_valid = False
        elif len(identifier) != 7:
            is_valid = False

    return is_valid


def _is_valid_new_style_arxiv_id(identifier):
    """Determine if the given identifier is a valid new style arXiv ID."""

    is_valid = True
    if len(identifier) < 9 or len(identifier) > 10:
        is_valid = False
    elif identifier.count('.') != 1:
        is_valid = False
    else:
        date, num = identifier.split('.')
        if any(map(lambda x: x not in string.digits, date + num)):
            is_valid = False
        elif len(date) != 4:
            is_valid = False
        elif int(date[2:4]) > 12:
            is_valid = False

    return is_valid


def is_valid_arxiv_id(identifier):
    """Determine whether or not the given identifier is a valid arXiv ID."""

    identifier = normalize(identifier)
    if identifier.lower().startswith('arxiv:'):
        identifier = identifier[len('arxiv:') :]

    valid_old_style_arxiv_id = _is_valid_old_style_arxiv_id(identifier)
    valid_new_style_arxiv_id = _is_valid_new_style_arxiv_id(identifier)

    return valid_old_style_arxiv_id or valid_new_style_arxiv_id


def normalize(identifier):
    """Remove the 'arxiv:' prefix or URL if it exists."""

    identifier = identifier.lower()
    if identifier.startswith('arxiv:'):
        identifier = identifier[len('arxiv:') :]
    else:
        pattern = re.compile(r'^(https?://)?(www\.)?arxiv\.org/')
        if pattern.match(identifier) is not None:
            stripped_identifier = pattern.split(identifier)[-1]
            if stripped_identifier.startswith('abs/'):
                identifier = stripped_identifier[len('abs/') :].rstrip('/')
            elif stripped_identifier.startswith('pdf/'):
                identifier = stripped_identifier[len('pdf/') :]
                if identifier.endswith('.pdf'):
                    identifier = identifier[: -len('.pdf')]

    return identifier

"""Functionality to interface with arXiv references."""

import re

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


def _is_valid_old_style_arxiv_id(identifier):
    """Determine if the given identifiier is a valid old style arXiv ID."""
    split_identifier = identifier.split('/')
    if len(split_identifier) != 2:
        return False
    subject, identifier = split_identifier

    split_subject = subject.split('.')
    if len(split_subject) > 2:
        return False
    elif len(split_subject) == 2:
        archive, version = split_subject
        if not version.isnumeric():
            return False
    else:
        archive = split_subject[0]

    if archive not in ARXIV_FIELDS:
        return False

    split_identifier = identifier.split('v')
    if len(split_identifier) > 2:
        return False
    elif len(split_identifier) == 2:
        identifier, version = split_identifier
    else:
        identifier = split_identifier[0]

    if not identifier.isnumeric():
        return False

    if len(identifier) != 7:
        return False

    year = int(identifier[:2])
    month = int(identifier[2:4])

    if not (month >= 1 and month <= 12):
        return False

    # Old version arXiv IDs don't exist before 1991 or after March 2007.
    if (year < 91 and year > 7) or (year == 7 and month > 3):
        return False

    return True


def _is_valid_new_style_arxiv_id(identifier):
    """Determine if the given identifier is a valid new style arXiv ID."""

    split_identifier = identifier.split('v')
    if len(split_identifier) > 2:
        return False
    elif len(split_identifier) == 2:
        identifier, version = split_identifier
        if not version.isnumeric():
            return False
    else:
        identifier = split_identifier[0]

    split_identifier = identifier.split('.')
    if len(split_identifier) != 2:
        return False

    prefix, suffix = split_identifier
    if not prefix.isnumeric() or not suffix.isnumeric():
        return False

    if len(prefix) != 4 or len(suffix) not in {4, 5}:
        return False

    month = prefix[2:4]
    if int(month) > 12:
        return False

    return True


def is_arxiv(identifier):
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

"""Module to check the validity of DOIs."""


def is_doi(identifier):
    """Determine whether the given identifier has a valid DOI format."""
    if not isinstance(identifier, str):
        return False

    identifier = identifier.lower()
    identifier = identifier.split('/')
    if len(identifier) < 2:
        return False

    if not identifier[0] or not identifier[1]:
        return False

    prefix = identifier[0]

    prefix = prefix.split('.')
    if len(prefix) < 2:
        return False

    if any(map(lambda x: not x.isnumeric(), prefix)):
        return False

    if prefix[0] != '10':
        return False

    return int(prefix[1]) >= 1000

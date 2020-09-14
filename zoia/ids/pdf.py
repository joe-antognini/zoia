"""Module to check whether an identifier is a PDF."""

import os


def is_pdf(identifier):
    """Check whether an idenitfier is a PDF."""
    if not os.path.isfile(identifier):
        return False

    with open(identifier, 'rb') as fp:
        return fp.read(4) == b'%PDF'

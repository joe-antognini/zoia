"""Functionality to interact with PDFs."""

import re

from pdfminer.high_level import extract_text


def get_doi_from_pdf(pdf_file):
    """Try to figure out the DOI of a paper from its PDF.

    This will do a basic search through the PDF to find any instances of a
    string like 'doi:10.XXXX/XXXXXX' in the document.  This will return the
    first valid DOI found.

    Args:
        pdf_file: str or file-like object
            Either the PDF filename or a file-like object with the PDF.

    Returns:
        doi: str
            The DOI.

    """
    text = extract_text(pdf_file)
    pattern = re.compile(
        r'(doi:\s*)(10\.[1-9][0-9]{3}[^\s]*/[^\s]*)', re.IGNORECASE
    )
    match = pattern.search(text)
    return match.groups()[1] if match is not None else None

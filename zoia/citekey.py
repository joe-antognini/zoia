"""Functions to create a unique citekey."""

import string

import zoia.metadata
import zoia.normalization

# TODO: Add functionality for other citekey styles.

# Ignore common words in the title when generating a citekey.
# TODO: Expand this list.
TITLE_WORD_BLACKLIST = {'a', 'an', 'are', 'is', 'of', 'on', 'the'}


def _get_title_start(title):
    """Get the first non-blacklisted word in the title."""
    title_words = map(lambda x: x.lower(), title.split())
    # TODO: Normalize the title for LaTeX characters.
    for word in title_words:
        if word not in TITLE_WORD_BLACKLIST:
            return word

    return title_words[0]


def _apply_citekey_format(
    name_string, year, first_word_of_title, identifier=None
):
    """Create a citekey in the appropriate format."""
    citekey = (
        f'{name_string}{year}'
        f'{identifier if identifier else ""}-{first_word_of_title}'
    )
    return zoia.normalization.normalize_string(citekey)


def _generate_identifiers():
    i = 1
    while True:
        identifiers = []
        j = i
        while j >= 0:
            identifiers.append(string.ascii_lowercase[j % 26])
            j = j // 26 - 1
        identifiers = identifiers[::-1]
        i += 1
        yield ''.join(identifiers)


def create_citekey(metadatum):
    """Create a unique citekey for the object."""
    # TODO: Expand this docstring.

    n_citekey_authors = 2 if len(metadatum.authors) == 2 else 1
    last_names = [
        elem[1].split() for elem in metadatum.authors[:n_citekey_authors]
    ]
    normalized_names = map('-'.join, last_names)
    name_string = '+'.join(normalized_names)
    if len(metadatum.authors) > 2:
        name_string += '+'
    year = metadatum.year % 100
    first_word_of_title = _get_title_start(metadatum.title)

    proposed_citekey = _apply_citekey_format(
        name_string, year, first_word_of_title
    )

    metadata = zoia.metadata.load_metadata()

    # TODO: Add a note to the README that this behavior is currently resolving
    # collisions by the order the reference was added to zoia, not by the
    # original date or title.  (This should be user-configurable.)
    if proposed_citekey in metadata:
        for identifier in _generate_identifiers():
            proposed_citekey = _apply_citekey_format(
                name_string, year, first_word_of_title, identifier
            )
            if proposed_citekey not in metadata:
                break

    return proposed_citekey

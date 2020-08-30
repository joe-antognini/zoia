"""Functions to create a unique citekey."""

import unicodedata

import zoia.metadata

# TODO: Add functionality for other citekey styles.

# Ignore common words in the title when generating a citekey.
# TODO: Expand this list.
TITLE_WORD_BLACKLIST = {'a', 'an', 'are', 'is', 'of', 'on', 'the'}


def _strip_diacritics(s):
    """Remove diacritics from the string."""
    return ''.join(
        [
            char for char in unicodedata.normalize('NFD', s)
            if unicodedata.category(char) != 'Mn'
        ]
    )


def _normalize_string(s):
    """Remove diacritics and return a lower-case version of the string."""
    s = _strip_diacritics(s)
    return s.lower()


def _get_last_name(name):
    """Attempt to determine the last name."""
    names = name.split()

    last_names = []
    if len(names) == 1:
        last_names.append(name)
    else:
        for elem in reversed(names[1:]):
            if '.' in elem:
                break
            else:
                last_names.append(elem)
    return last_names[::-1]


def _get_title_start(title):
    """Get the first non-blacklisted word in the title."""
    title_words = map(lambda x: x.lower(), title.split())
    # TODO: Normalize the title for LaTeX characters.
    for word in title_words:
        if word not in TITLE_WORD_BLACKLIST:
            return word

    return title_words[0]


def _propose_citekey(joined_names, year, first_word_of_title):
    citekey = f'{joined_names}{year}-{first_word_of_title}'
    return _normalize_string(citekey)


def _resolve_collisions(proposed_citekey):
    """Fix potential collisions between proposed and existing citekeys."""
    metadata = zoia.metadata.load_metadata()
    if proposed_citekey in metadata:
        # TODO
        pass

    # TODO: Handle the case of an existing key of the form "nameYYa-title".

    # TODO: If there is a collision, figure out which key should go first based
    # on date.

    # TODO: Figure out the best way to return information that other citekeys
    # need to be renamed.


def create_citekey(metadatum):
    """Create a unique citekey for the object."""
    # TODO: Expand this docstring.

    last_names = map(_get_last_name, metadatum.authors[:3])
    normalized_names = map('-'.join, last_names)
    joined_names = '+'.join(normalized_names)
    year = metadatum.year % 100
    first_word_of_title = _get_title_start(metadatum.title)
    citekey = _propose_citekey(
        joined_names, year, collision_count, first_word_of_title
    )

    # TODO: Handle collisions.  Note that this is a little complicated because
    # it's possible that there had already been a collision, in which case the
    # original citekey got renamed to "nameYYa-title", leaving the original
    # free.
    return citekey

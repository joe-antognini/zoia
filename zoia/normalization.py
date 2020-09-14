"""Utilities to normalize strings."""

import string
import unicodedata


def strip_diacritics(s):
    """Remove diacritics from the string."""
    return ''.join(
        [
            char
            for char in unicodedata.normalize('NFD', s)
            if unicodedata.category(char) != 'Mn'
        ]
    )


def normalize_name(s):
    """Remove diacritics and return a lower-case version of the string."""
    s = strip_diacritics(s)
    return s.lower()


def split_name(name):
    """Split a name into a list of a first and last name."""
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
    last_name = ' '.join(reversed(last_names))
    first_name = ' '.join(names[: len(names) - len(last_names)])
    return [first_name, last_name]


def normalize_title_word(word):
    """Normalize a word in a title."""
    good_characters = string.ascii_lowercase + string.digits
    word = word.lower()
    return ''.join(filter(lambda x: x in good_characters, word))

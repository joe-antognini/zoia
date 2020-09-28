"""Tools to interact with the library metadata."""

from abc import ABC
from abc import abstractmethod
from dataclasses import dataclass
from typing import List

from zoia.parse.normalization import split_name


@dataclass
class Metadatum:
    entry_type: str
    title: str
    authors: List[str]
    year: int

    @classmethod
    def from_dict(cls, d):
        return cls(
            entry_type=d.get('entry_type', 'misc'),
            title=d['title'],
            authors=d['authors'],
            year=d['year'],
        )

    def to_dict(self):
        return {
            key: getattr(self, key) for key in self.__dataclass_fields__.keys()
        }

    def __post_init__(self):
        if not isinstance(self.authors, list):
            raise TypeError(
                f'authors attribute must be a list, but got type '
                f'{type(self.authors)}.'
            )

        self.authors = [
            split_name(elem) if isinstance(elem, str) else elem
            for elem in self.authors
        ]

    def __str__(self):
        if len(self.authors) == 1:
            author_str = self.authors[0][1]
        elif len(self.authors) == 2:
            author_str = self.authors[0][1] + ' & ' + self.authors[1][1]
        else:
            author_str = self.authors[0][1] + ' et al.'

        s = f'{author_str} ({self.year}), '
        title_str = []
        str_len = len(s) + 2  # Quotation marks around the title add two chars.
        for i_word, word in enumerate(self.title.split()):
            str_len += len(word) + 1
            title_str.append(word)
            # TODO: Make this configurable.
            if str_len > 65 and i_word > 2:
                title_str.append('...')
                break
        title_str = ' '.join(title_str)
        return s + f'"{title_str}"'


class Metadata(ABC):
    """An abstract class with the API to interact with metadata."""

    @abstractmethod
    def __init__(self, config):
        """Initialize the metadata database."""

    @abstractmethod
    def __contains__(self, citekey):
        """Determine whether the citekey exists in the library."""

    @abstractmethod
    def __getitem__(self, citekey):
        """Load the metadata for a citekey."""

    @abstractmethod
    def write(self):
        """Write the metadata for the library to disk.

        Note that this will overwrite any existing metadata.

        """

    @abstractmethod
    def append(self, key, value):
        """Append the given data to the metadata file."""

    @abstractmethod
    def replace(self, key, value):
        """Replace the data for a given key."""

    @abstractmethod
    def rename_key(self, old_key, new_key):
        """Rename a citekey in the metadata."""

    @abstractmethod
    def arxiv_id_exists(self):
        """Return a set of all existing arXiv identifiers."""

    @abstractmethod
    def isbn_exists(self):
        """Return a set of all existing ISBNs."""

    @abstractmethod
    def doi_exists(self):
        """Return a set of all existing DOIs."""

    @abstractmethod
    def pdf_md5_hash_exists(self):
        """Return a set of all the MD5 hashes of existing PDFs."""


def get_metadata(config):
    """Get the appropriate metadata class from the config dataclass."""

    import zoia.backend.json
    import zoia.backend.sqlite

    if config.backend == zoia.backend.config.ZoiaBackend.JSON:
        return zoia.backend.json.JSONMetadata(config)
    if config.backend == zoia.backend.config.ZoiaBackend.SQLITE:
        return zoia.backend.sqlite.SQLiteMetadata(config)
    else:
        raise NotImplementedError(
            f'Backend {config.backend.value} not implemented yet.'
        )

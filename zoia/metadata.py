"""Tools to interact with the library metadata."""

import json
import os
from dataclasses import dataclass
from typing import List

from zoia.config import get_library_root
from zoia.config import ZOIA_METADATA_FILENAME


@dataclass
class Metadatum:
    title: str
    authors: List[str]
    year: int

    @classmethod
    def from_dict(cls, d):
        return cls(
            title=d['title'],
            authors=d['authors'],
            year=d['year'],
        )


def load_metadata():
    """Load the metadata for the library."""

    library_root = get_library_root()
    if library_root is None:
        return {}

    metadata_filename = os.path.join(library_root, ZOIA_METADATA_FILENAME)
    with open(metadata_filename) as fp:
        metadata = json.load(fp)

    return metadata


def _write_metadata(metadata):
    """Write the metadata for the library to disk.

    Note that this will overwrite any existing metadata.

    """
    library_root = get_library_root()
    if library_root is None:
        raise RuntimeError('No library root set.  Cannot write metadata!')

    metadata_filename = os.path.join(library_root, ZOIA_METADATA_FILENAME)
    with open(metadata_filename, 'w') as fp:
        json.dump(metadata, fp, indent=4, sort_keys=True)


def initialize_metadata():
    """Initialize an empty metadata file on the disk."""
    library_root = get_library_root()
    metadata_filename = os.path.join(library_root, ZOIA_METADATA_FILENAME)

    if os.path.exists(metadata_filename):
        raise RuntimeError(
            f'Metadata file already exists at {metadata_filename}'
        )

    _write_metadata({})


def append_metadata(key, value):
    """Append the given data to the metadata file."""
    metadata = load_metadata()
    if key in metadata:
        raise KeyError(f'Key {key} is already present.')

    metadata[key] = value
    _write_metadata(metadata)


def rename_key(old_key, new_key):
    """Rename a citekey in the metadata."""
    metadata = load_metadata()

    if new_key in metadata:
        raise KeyError(f'Key {new_key} is already present.')

    metadata[new_key] = metadata.pop(old_key)
    _write_metadata(metadata)


def get_arxiv_ids():
    """Return a set of all existing arXiv identifiers."""
    metadata = load_metadata()
    return {
        elem['arxiv_id'] for elem in metadata.values() if 'arxiv_id' in elem
    }

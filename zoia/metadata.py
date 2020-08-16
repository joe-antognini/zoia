"""Tools to interact with the library metadata."""

import json
import os
from typing import List

from zoia.config import get_library_root
from zoia.config import ZOIA_METADATA_FILENAME


@dataclass
class Metadatum:
    title: str
    # TODO: Split out first and last names.
    authors: List[str]
    year: int


def load_metadata():
    """Load the metadata for the library."""

    library_root = get_library_root()
    if library_root is None:
        return {}

    metadata_filename = os.path.join(library_root, ZOIA_METADATA_FILENAME)
    with open(metadata_filename) as fp:
        metadata = json.load(fp)

    return metadata


def append_metadata(key, value):
    """Append the given data to the metadata file."""
    metadata = load_metadata()
    metadata[key] = value
    write_metadata(metadata)


def write_metadata(metadata):
    """Write the metadata for the library to disk."""

    library_root = get_library_root()
    if library_root is None:
        raise RuntimeError('No library root set.  Cannot write metadata!')

    metadata_filename = os.path.join(library_root, ZOIA_METADATA_FILENAME)
    with open(metadata_filename, 'w') as fp:
        json.dump(metadata, fp, indent=4, sort_keys=True)

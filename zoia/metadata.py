"""Tools to interact with the library metadata."""

import json
import os

from zoia.config import get_library_root
from zoia.config import ZOIA_METADATA_FILENAME


def load_metadata():
    """Load the metadata for the library."""

    metadata_filename = os.path.join(
        get_library_root(), ZOIA_METADATA_FILENAME
    )
    with open(metadata_filename) as fp:
        metadata = json.load(fp)

    return metadata


def write_metadata(metadata):
    """Write the metadata for the library to disk."""

    metadata_filename = os.path.join(
        get_library_root(), ZOIA_METADATA_FILENAME
    )
    with open(metadata_filename, 'w') as fp:
        json.dump(metadata, fp, indent=2)

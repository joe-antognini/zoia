"""Tools to interact with a simple JSON backend."""

import json
import os

import zoia.backend.metadata


class JSONMetadata(zoia.backend.metadata.Metadata):
    def __init__(self, config):
        """Load the metadata for the library into memory."""

        self.config = config
        self._metadata = {}
        self.metadata_filename = None
        self.metadata_filename = os.path.join(config.db_root, 'metadata.json')

        if os.path.exists(self.metadata_filename):
            with open(self.metadata_filename) as fp:
                self._metadata = json.load(fp)

    def __contains__(self, citekey):
        """Determine whether the citekey exists in the library."""

        return citekey in self._metadata

    def __getitem__(self, citekey):
        """Load the metadata for a citekey."""

        return self._metadata[citekey]

    def write(self):
        """Write the metadata for the library to disk.

        Note that this will overwrite any existing metadata.

        """
        if self.config.db_root is None:
            raise RuntimeError('No library root set.  Cannot write metadata!')

        with open(self.metadata_filename, 'w') as fp:
            json.dump(self._metadata, fp, indent=4, sort_keys=True)

    def append(self, key, value):
        """Append the given data to the metadata file."""
        if key in self._metadata:
            raise KeyError(f'Key {key} is already present.')

        self._metadata[key] = value
        self.write()

    def replace(self, key, value):
        """Replace the data for a given key."""
        if key not in self._metadata:
            raise KeyError(f'Key {key} not present.')

        self._metadata[key] = value
        self.write()

    def rename_key(self, old_key, new_key):
        """Rename a citekey in the metadata."""
        if new_key in self._metadata:
            raise KeyError(f'Key {new_key} is already present.')

        self._metadata[new_key] = self._metadata.pop(old_key)
        self.write()

    def arxiv_ids(self):
        """Return a set of all existing arXiv identifiers."""
        return {
            elem['arxiv_id']
            for elem in self._metadata.values()
            if 'arxiv_id' in elem
        }

    def isbns(self):
        """Return a set of all existing ISBNs."""
        return {
            elem['isbn'] for elem in self._metadata.values() if 'isbn' in elem
        }

    def dois(self):
        """Return a set of all existing DOIs."""
        return {
            elem['doi'] for elem in self._metadata.values() if 'doi' in elem
        }

    def pdf_md5_hashes(self):
        """Return a set of all the MD5 hashes of existing PDFs."""
        return {
            elem['pdf_md5']
            for elem in self._metadata.values()
            if 'pdf_md5' in elem
        }

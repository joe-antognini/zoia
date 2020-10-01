"""Tools to interact with a simple JSON backend."""

import json
import os

import zoia.backend.metadata


class JSONMetadata(zoia.backend.metadata.Metadata):
    """A class to interact with the JSON backend."""

    def __init__(self, config):
        """Load the metadata for the library into memory."""

        self.config = config
        self._metadata = {}
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

    def arxiv_id_exists(self, arxiv_id):
        """Return a set of all existing arXiv identifiers."""
        arxiv_ids = {elem.get('arxiv_id') for elem in self._metadata.values()}
        return arxiv_id in arxiv_ids

    def isbn_exists(self, isbn):
        """Return a set of all existing ISBNs."""
        isbns = {elem.get('isbn') for elem in self._metadata.values()}
        return isbn in isbns

    def doi_exists(self, doi):
        """Return a set of all existing DOIs."""
        dois = {elem.get('doi') for elem in self._metadata.values()}
        return doi in dois

    def pdf_md5_hash_exists(self, pdf_md5):
        """Return a set of all the MD5 hashes of existing PDFs."""
        pdf_md5s = {elem.get('pdf_md5') for elem in self._metadata.values()}
        return pdf_md5 in pdf_md5s

"""Functions to create a unique citekey."""

import zoia.metadata

# TODO: Add functionality for other citekey styles.


def create_citekey(metadatum):
    """Create a unique citekey for the object."""
    # TODO: Expand this docstring.

    existing_metadata = zoia.metadata.load_metadata()
    # TODO: Figure out how to get first and last names separately.
    proposed_citekey = 

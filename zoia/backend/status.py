"""Functionality to display status messages."""

from halo import Halo


class StatusMessage:
    """A generic class to provide status updates to the UI.

    At the moment only a text user interface is supported so this simply passes
    messages along to `Halo`.

    """

    def __init__(self, text=None):
        self.spinner = Halo(text, spinner='dots')

    def __enter__(self, text=None):
        self.spinner.__enter__()
        return self

    def __exit__(self, exc_type, exc_value, exc_traceback):
        self.spinner.__exit__(exc_type, exc_value, exc_traceback)

    def update(self, text):
        self.spinner.text = text

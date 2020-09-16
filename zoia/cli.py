"""Entry-point to the zoia CLI."""

import click

from zoia.add import add
from zoia.edit import edit
from zoia.init import init
from zoia.note import note
from zoia.open import open_


@click.group()
@click.version_option()
def zoia():
    """The main entry point into `zoia`."""


zoia.add_command(add)
zoia.add_command(edit)
zoia.add_command(init)
zoia.add_command(note)
zoia.add_command(open_)

if __name__ == '__main__':
    zoia()

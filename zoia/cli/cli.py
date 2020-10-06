"""Entry-point to the zoia CLI."""

import click

from zoia.cli.add import add
from zoia.cli.config import config
from zoia.cli.edit import edit
from zoia.cli.init import init
from zoia.cli.note import note
from zoia.cli.open import open_
from zoia.cli.tag import tag


@click.group()
@click.version_option()
def zoia():
    """The main entry point into `zoia`."""


zoia.add_command(add)
zoia.add_command(config)
zoia.add_command(edit)
zoia.add_command(init)
zoia.add_command(note)
zoia.add_command(open_)
zoia.add_command(tag)

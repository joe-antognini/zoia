"""Entry-point to the zoia CLI."""

import click

from zoia.init import init


@click.group()
def zoia():
    """The main entry point into `zoia`."""


zoia.add_command(init)

if __name__ == '__main__':
    zoia()

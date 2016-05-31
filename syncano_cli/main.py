# -*- coding: utf-8 -*-
from __future__ import print_function

from ConfigParser import ConfigParser

import click
from syncano.exceptions import SyncanoException
from syncano_cli.commands import top_level
from syncano_cli.parse_to_syncano.commands import top_transfer
from syncano_cli.sync.commands import top_sync

ACCOUNT_KEY = ''
ACCOUNT_CONFIG = ConfigParser()


cli = click.CommandCollection(
    sources=[
        top_level,
        top_sync,
        top_transfer,
    ])

if __name__ == "__main__":
    try:
        cli(obj={})
    except SyncanoException as error:
        click.echo(error)

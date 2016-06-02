# -*- coding: utf-8 -*-
from __future__ import print_function

import sys

sys.path.append('/home/sopalczy/projects/syncano/syncano-cli/')
sys.path.append('/home/sopalczy/projects/syncano/syncano-python/')

import click
from syncano.exceptions import SyncanoException
from syncano_cli.commands import top_level
from syncano_cli.parse_to_syncano.commands import top_migrate
from syncano_cli.sync.commands import top_sync

ACCOUNT_KEY = ''

cli = click.CommandCollection(
    sources=[
        top_level,
        top_sync,
        top_migrate,
    ])


def main():
    try:
        cli(obj={})
    except SyncanoException as error:
        click.echo(error)
        sys.exit(1)


if __name__ == "__main__":
    main()

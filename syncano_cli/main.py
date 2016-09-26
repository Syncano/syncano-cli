# -*- coding: utf-8 -*-
from __future__ import print_function

import click
from click import ClickException
from syncano.exceptions import SyncanoException
from syncano_cli.account.commands import top_account
from syncano_cli.base.exceptions import CLIBaseException, SyncanoLibraryException
from syncano_cli.commands import top_level
from syncano_cli.config_commands.commands import top_config
from syncano_cli.custom_sockets.commands import top_sockets
from syncano_cli.execute.commands import top_execute
from syncano_cli.hosting.commands import top_hosting
from syncano_cli.init.commands import top_init
from syncano_cli.instance.commands import top_instance
from syncano_cli.parse_to_syncano.commands import top_migrate
from syncano_cli.sync.commands import top_sync

cli = click.CommandCollection(
    sources=[
        top_account,
        top_config,
        top_execute,
        top_hosting,
        top_init,
        top_instance,
        top_level,
        top_migrate,
        top_sync,
        top_sockets,

    ],
)


def main():
    try:
        cli(obj={})
    except SyncanoException as e:
        raise SyncanoLibraryException(e.reason)
    except ClickException:
        raise CLIBaseException('CLI exception.')
    else:
        raise

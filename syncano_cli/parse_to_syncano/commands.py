# -*- coding: utf-8 -*-
import sys

import click
from syncano_cli.base.command import BaseCommand
from syncano_cli.base.options import ErrorOpt, SpacedOpt
from syncano_cli.parse_to_syncano.config import read_config
from syncano_cli.parse_to_syncano.migrations.transfer import SyncanoTransfer
from syncano_cli.parse_to_syncano.moses import check_configuration, force_configuration_overwrite, print_configuration


@click.group()
def top_migrate():
    pass


@top_migrate.group()
@click.pass_context
@click.option('--config', help=u'Account configuration file.')
def migrate(context, config):
    """Migrate Parse data to Syncano."""
    command = BaseCommand(config)
    context.obj['config'] = config
    context.obj['command'] = command


@migrate.command()
@click.pass_context
def parse(context):
    """Synchronize the Parse data objects with Syncano data objects."""
    command = context.obj['command']
    config = read_config(command.config.global_config)
    check_configuration(config, command.config.global_config_path, silent=True)
    application_id = config.get('P2S', 'PARSE_APPLICATION_ID')
    instance_name = config.get('P2S', 'SYNCANO_INSTANCE_NAME')
    confirmation = command.prompter.confirm(
        'Are you sure you want to copy your data from Parse application ({application_id})'
        ' to the Syncano Instance ({instance_name})?: '.format(
            application_id=application_id,
            instance_name=instance_name)
    )

    if not confirmation:
        command.formatter.write('Transfer aborted.', ErrorOpt(), SpacedOpt())
        sys.exit(1)

    moses = SyncanoTransfer(config)
    moses.through_the_red_sea()


@migrate.command()
@click.pass_context
@click.option('--current', is_flag=True, default=False, help="Show current configuration.")
@click.option('--force', is_flag=True, default=False, help="Force to overwrite previous config.")
def configure(context, current, force):
    """
    Configure the data needed for connection between Parse and Syncano.

    PARSE_MASTER_KEY - is a parse master key;

    PARSE_APPLICATION_ID - is a parse application ID that you want to migrate;

    SYNCANO_ADMIN_API_KEY - is a Syncano API key (account key);

    SYNCANO_INSTANCE_NAME - is a instance name; to this instance data will be migrated;
    """
    command = context.obj['command']
    command.formatter.write('See details or set up your configuration.', SpacedOpt())
    config = read_config(command.config)
    if current:
        print_configuration(config)
    elif force:
        force_configuration_overwrite(config, command.config.global_config_path)
    else:
        check_configuration(config, command.config.global_config_path)
    command.formatter.empty_line()

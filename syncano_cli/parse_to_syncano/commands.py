# -*- coding: utf-8 -*-
import click
from syncano_cli.config import ACCOUNT_CONFIG_PATH
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
    """
    Migrate Parse data to Syncano
    """
    config = config or ACCOUNT_CONFIG_PATH
    context.obj['config'] = config


@migrate.command()
@click.pass_context
def parse(context):
    """
        Synchronize the Parse data objects with Syncano data objects;
        """
    config = read_config(config_path=context.obj['config'])
    check_configuration(config, silent=True)
    application_id = config.get('P2S', 'PARSE_APPLICATION_ID')
    instance_name = config.get('P2S', 'SYNCANO_INSTANCE_NAME')
    confirmation = click.confirm(
        'Are you sure you want to copy your data from Parse application ({application_id})'
        ' to the Syncano Instance ({instance_name})?: '.format(
            application_id=application_id,
            instance_name=instance_name)
    )

    if not confirmation:
        click.echo('INFO: Transfer aborted.')
        return

    moses = SyncanoTransfer(config)
    moses.through_the_red_sea()


@migrate.command()
@click.pass_context
@click.option('--current', is_flag=True, default=False, help="Show current configuration.")
@click.option('--force', is_flag=True, default=False, help="Force to overwrite previous config.")
def configure(context, current, force):
    """
    Configure the data needed for connection between Parse and Syncano;
    """
    config = read_config(config_path=context.obj['config'])
    if current:
        print_configuration(config)
    elif force:
        force_configuration_overwrite(config)
    else:
        check_configuration(config)

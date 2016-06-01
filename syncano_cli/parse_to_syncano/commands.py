# -*- coding: utf-8 -*-
import click
from syncano_cli import LOG
from syncano_cli.config import ACCOUNT_CONFIG_PATH
from syncano_cli.parse_to_syncano.config import read_config
from syncano_cli.parse_to_syncano.migrations.transfer import SyncanoTransfer
from syncano_cli.parse_to_syncano.moses import check_configuration, force_configuration_overwrite, print_configuration


@click.group()
@click.pass_context
def top_transfer(context):
    pass


@top_transfer.group()
@click.pass_context
@click.option('--config', help=u'Account configuration file.')
def transfer(context, config):
    """
    Command for transfer data to Syncano
    """
    config = config or ACCOUNT_CONFIG_PATH
    context.obj['config'] = config


@transfer.command()
@click.pass_context
def parse(context):
    """
        Synchronize the parse data object with syncano data objects;
        """
    config = read_config(config_path=context.obj['config'])
    check_configuration(config, silent=True)
    application_id = config.get('P2S', 'PARSE_APPLICATION_ID')
    instance_name = config.get('P2S', 'SYNCANO_INSTANCE_NAME')
    confirmation = raw_input(
        'Are you sure you want to copy your data from Parse application ({application_id})'
        ' to the Syncano Instance ({instance_name})? Y/N [Y]: '.format(
            application_id=application_id,
            instance_name=instance_name)
    ) or 'Y'

    if confirmation not in ['Y', 'YES', 'y', 'yes']:
        LOG.info('Transfer aborted.')
        return

    moses = SyncanoTransfer(config)
    moses.through_the_red_sea()


@transfer.command()
@click.pass_context
@click.option('--current/--no-current', default=False, help="Show current configuration.")
@click.option('--force/--no-force', default=False, help="Force to overwrite previous config.")
def configure(context, current, force):
    """
    Configure the data needed for connection to the parse and syncano;
    """
    config = read_config(config_path=context.obj['config'])
    if current:
        print_configuration(config)
    elif force:
        force_configuration_overwrite(config)
    else:
        check_configuration(config)

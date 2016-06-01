# -*- coding: utf-8 -*-
import click
from syncano_cli import LOG
from syncano_cli.parse_to_syncano.config import config
from syncano_cli.parse_to_syncano.migrations.transfer import SyncanoTransfer
from syncano_cli.parse_to_syncano.moses import check_configuration, force_configuration_overwrite, print_configuration


@click.group()
@click.pass_context
def top_transfer(context):
    pass


@top_transfer.group()
@click.pass_context
def transfer(context):
    """
    Command for transfer data to Syncano
    """
    pass


@transfer.command()
@click.pass_context
def parse(context):
    """
        Synchronize the parse data object with syncano data objects;
        """
    check_configuration(silent=True)
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

    transfer = SyncanoTransfer()
    transfer.through_the_red_sea()


@transfer.command()
@click.pass_context
@click.option('--current/--no-current', default=False, help="Show current configuration.")
@click.option('--force/--no-force', default=False, help="Force to overwrite previous config.")
def configure(context, current, force):
    """
    Configure the data needed for connection to the parse and syncano;
    """
    if current:
        print_configuration()
    elif force:
        force_configuration_overwrite()
    else:
        check_configuration()

# -*- coding: utf-8 -*-
import six
from syncano_cli import LOG
from syncano_cli.commands_base import CommandContainer, argument
from syncano_cli.parse_to_syncano.config import config
from syncano_cli.parse_to_syncano.migrations.transfer import SyncanoTransfer
from syncano_cli.parse_to_syncano.moses import check_configuration, force_configuration_overwrite, print_configuration

COMMAND_NAMESPACE = 'import'


class Parse(six.with_metaclass(CommandContainer)):
    namespace = COMMAND_NAMESPACE

    @classmethod
    def run(self, context):
        """
        Synchronize the parse data object with syncano data objects;
        """
        check_configuration(silent=True)
        application_id = config.get('P2S', 'PARSE_APPLICATION_ID')
        instance_name = config.get('P2S', 'SYNCANO_INSTANCE_NAME')
        confirmation = raw_input('Are you sure you want to copy your data from Parse application ({application_id})'
                                 ' to the Syncano Instance ({instance_name})? Y/N [Y]: '.format(
                                     application_id=application_id,
                                     instance_name=instance_name)
                                 ) or 'Y'

        if confirmation not in ['Y', 'YES', 'y', 'yes']:
            LOG.info('Transfer aborted.')
            return

        transfer = SyncanoTransfer()
        transfer.through_the_red_sea()


class Configure(six.with_metaclass(CommandContainer)):
    namespace = COMMAND_NAMESPACE

    @classmethod
    @argument('-c', '--current', action='store_true', help="Show current configuration.")
    @argument('-f', '--force', action='store_true', help="Force to overwrite previous config.")
    def run(self, context):
        """
        Configure the data needed for connection to the parse and syncano;
        """
        if context.current:
            print_configuration()
        elif context.force:
            force_configuration_overwrite()
        else:
            check_configuration()

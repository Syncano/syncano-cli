# -*- coding: utf-8 -*-
import sys

import click
from syncano_cli.base.connection import create_connection
from syncano_cli.config import ACCOUNT_CONFIG_PATH
from syncano_cli.hosting.utils import HostingCommands
from syncano_cli.logger import get_logger

LOG = get_logger('syncano-hosting')


@click.group()
def top_hosting():
    pass


@top_hosting.command()
@click.option('--config', help=u'Account configuration file.')
@click.argument('instance_name', envvar='SYNCANO_INSTANCE')
@click.option('--list', is_flag=True, help='List available hostings in instance.')
@click.option('--create', is_flag=True, help='Create hosting with specified domain.')
@click.option('--label', required=False)
@click.option('--list-files', is_flag=True, help='List files within the hosting.')
@click.option('--publish', type=str, help='Publish files from the local directory to the Syncano Hosting.')
@click.argument('domain', required=False)
def hosting(config, instance_name, list, create, label, list_files, publish, domain):
    """
    Execute script endpoint in given instance
    """

    def validate_domain(domain):
        if not domain:
            LOG.info('Domain is required if you want to list hosting files.')
            sys.exit(1)

    config = config or ACCOUNT_CONFIG_PATH
    try:
        connection = create_connection(config)
        instance = connection.Instance.please.get(name=instance_name)

        hosting_commands = HostingCommands(instance)

        if list:
            hosting_list = hosting_commands.list_hosting()
            hosting_commands.print_hosting_list(hosting_list)

        if list_files:
            validate_domain(domain)
            hosting_files = hosting_commands.list_hosting_files(domain=domain)
            hosting_commands.print_hosting_files(hosting_files)

        if publish:
            validate_domain(domain)
            uploaded_files = hosting_commands.publish(domain=domain, base_dir=publish)
            hosting_commands.print_hosting_files(uploaded_files)

        if create:
            validate_domain(domain)
            created_hosting = hosting_commands.create_hosting(domain=domain, label=label)
            hosting_commands.print_hostng_created_info(created_hosting)

    except Exception as e:
        LOG.error(e)
        sys.exit(1)

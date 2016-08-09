# -*- coding: utf-8 -*-
import os
import sys

import click
from syncano_cli.base.connection import create_connection
from syncano_cli.config import ACCOUNT_CONFIG_PATH
from syncano_cli.hosting.utils import HostingCommands


@click.group()
def top_hosting():
    pass


@top_hosting.command()
@click.option('--config', help=u'Account configuration file.')
@click.argument('instance_name', envvar='SYNCANO_INSTANCE')
@click.option('--list-files', is_flag=True, help='List files within the hosting.')
@click.option('--publish', type=str, help='Publish files from the local directory to the Syncano Hosting.')
def hosting(config, instance_name, list_files, publish):
    """
    Execute script endpoint in given instance
    """

    def validate_domain(provided_domain=None):
        return 'default' if not provided_domain else provided_domain

    def validate_publish(base_dir):
        if not os.path.isdir(base_dir):
            click.echo(u'ERROR: You should provide a project root directory here.')
            sys.exit(1)

    config = config or ACCOUNT_CONFIG_PATH
    try:
        connection = create_connection(config)
        instance = connection.Instance.please.get(name=instance_name)

        hosting_commands = HostingCommands(instance)

        if list_files:
            domain = validate_domain()
            click.echo(u'INFO: List the hosting files: {} in instance: {}'.format(domain, instance_name))
            hosting_files = hosting_commands.list_hosting_files(domain=domain)
            hosting_commands.print_hosting_files(hosting_files)

        if publish:
            domain = validate_domain()
            click.echo(u'INFO: Publish the hosting files: {} in instance: {}'.format(domain, instance_name))
            validate_publish(base_dir=publish)
            uploaded_files = hosting_commands.publish(domain=domain, base_dir=publish)
            hosting_commands.print_hosting_files(uploaded_files)

    except Exception as e:
        click.echo(u'ERROR: {}'.format(e))
        sys.exit(1)

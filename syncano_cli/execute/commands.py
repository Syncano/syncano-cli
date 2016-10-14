# -*- coding: utf-8 -*-

import click
from syncano_cli.execute.command import ExecuteCommand


@click.group()
def top_execute():
    pass


@top_execute.command()
@click.option('--config', help=u'Account configuration file.')
@click.option('--instance-name', help=u'Instance name.')
@click.argument('script_endpoint_name')
@click.option('-d', '--data', help=u'A data to be sent as payload: key=value', multiple=True)
def execute(config, instance_name, script_endpoint_name, data):
    """Execute Script endpoint in given Instance."""
    execute_command = ExecuteCommand(config)
    execute_command.set_instance(instance_name)
    execute_command.execute(script_endpoint_name, data)

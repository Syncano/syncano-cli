# -*- coding: utf-8 -*-

import click
from syncano_cli.base.connection import get_instance
from syncano_cli.base.data_parser import parse_input_data

from .utils import print_response


@click.group()
def top_execute():
    pass


@top_execute.command()
@click.option('--config', help=u'Account configuration file.')
@click.option('--instance-name', help=u'Instance name.')
@click.argument('script_endpoint_name')
@click.option('-d', '--data', help=u'A data to be sent as payload: key=value', multiple=True)
def execute(config, instance_name, script_endpoint_name, data):
    """
    Execute script endpoint in given instance
    """
    instance = get_instance(config, instance_name)
    se = instance.script_endpoints.get(name=script_endpoint_name)
    data = parse_input_data(data)
    response = se.run(**data)
    print_response(response)

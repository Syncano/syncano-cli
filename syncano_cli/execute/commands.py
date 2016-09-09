# -*- coding: utf-8 -*-
import json

import click
from syncano_cli.base.connection import get_instance
from syncano_cli.base.exceptions import JSONParseException

from .utils import print_response


@click.group()
def top_execute():
    pass


@top_execute.command()
@click.option('--config', help=u'Account configuration file.')
@click.option('--instance-name', help=u'Instance name.')
@click.argument('script_endpoint_name')
@click.option('--payload', help=u'Script payload in JSON format.')
def execute(config, instance_name, script_endpoint_name, payload):
    """
    Execute script endpoint in given instance
    """
    instance = get_instance(config, instance_name)
    se = instance.script_endpoints.get(name=script_endpoint_name)
    try:
        data = json.loads((payload or '').strip() or '{}')
    except:
        raise JSONParseException()
    response = se.run(**data)
    print_response(response)

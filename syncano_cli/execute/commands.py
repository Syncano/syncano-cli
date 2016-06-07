# -*- coding: utf-8 -*-
from __future__ import print_function

import json
import sys
from ConfigParser import NoOptionError

import click
from syncano_cli import LOG

from .connection import create_connection


@click.group()
def top_execute():
    pass


@top_execute.command()
@click.option('--config', help=u'Account configuration file.')
@click.argument('instance_name', envvar='SYNCANO_INSTANCE')
@click.argument('script_endpoint_name')
@click.option('--payload', help=u'Script payload in JSON format.')
def execute(config, instance_name, script_endpoint_name, payload):
    """
    Execute script endpoint in given instance
    """
    try:
        connection = create_connection(config)
    except NoOptionError:
        LOG.error('Do a login first: syncano login.')
        sys.exit(1)
    instance = connection.Instance.please.get(instance_name)
    se = instance.script_endpoints.get(instance_name, script_endpoint_name)
    data = json.loads(payload.strip() or '{}')
    response = se.run(**data)
    print(json.dumps(response.result, indent=4, sort_keys=True))

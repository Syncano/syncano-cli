# -*- coding: utf-8 -*-
from __future__ import print_function

import sys
from ConfigParser import NoOptionError

import click
import json
from syncano_cli import LOG
from syncano.models.incentives import ScriptEndpoint

from .connection import create_instance_connection


@click.group()
def top_execute():
    pass


@top_execute.command()
@click.option('--config', help=u'Account configuration file.')
@click.argument('instance', envvar='SYNCANO_INSTANCE')
@click.argument('script_endpoint_name')
@click.option('--payload', help=u'Script payload in JSON format.')
def execute(config, instance, script_endpoint_name, payload):
    """
    Execute script endpoint in given instance
    """
    try:
        connection = create_instance_connection(config, instance)
    except NoOptionError:
        LOG.error('Do a login first: syncano login.')
        sys.exit(1)
    api_path = ScriptEndpoint._meta.endpoints['run']['path'].format(
        instance_name=instance, name=script_endpoint_name
    )
    data = json.loads(payload.strip() or '{}')
    result = connection.request('GET', api_path, data=data)
    print(json.dumps(result, indent=4, sort_keys=True))

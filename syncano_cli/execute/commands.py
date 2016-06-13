# -*- coding: utf-8 -*-
import json
import sys
from ConfigParser import NoOptionError

import click
from syncano.exceptions import SyncanoDoesNotExist
from syncano_cli.logger import get_logger

from .connection import create_connection
from .utils import print_response

LOG = get_logger('syncano-execute')


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
        instance = connection.Instance.please.get(instance_name)
        se = instance.script_endpoints.get(instance_name, script_endpoint_name)
        data = json.loads((payload or '').strip() or '{}')
        response = se.run(**data)
        print_response(response)
    except NoOptionError:
        LOG.error('Do a login first: syncano login.')
        sys.exit(1)
    except SyncanoDoesNotExist as e:
        LOG.error(e)
        sys.exit(1)
    except ValueError as e:
        LOG.error('Invalid payload format: {error}'.format(error=e))
        sys.exit(1)

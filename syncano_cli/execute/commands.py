# -*- coding: utf-8 -*-
import json
import sys
from ConfigParser import NoOptionError

import click
from syncano.exceptions import SyncanoDoesNotExist
from syncano_cli.base.connection import create_connection
from syncano_cli.config import ACCOUNT_CONFIG_PATH

from .utils import print_response


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
    config = config or ACCOUNT_CONFIG_PATH
    try:
        connection = create_connection(config)
        instance = connection.Instance.please.get(instance_name)
        se = instance.script_endpoints.get(instance_name, script_endpoint_name)
        data = json.loads((payload or '').strip() or '{}')
        response = se.run(**data)
        print_response(response)
    except NoOptionError:
        click.echo(u'ERROR: Do a login first: syncano login.')
        sys.exit(1)
    except SyncanoDoesNotExist as e:
        click.echo(u'ERROR: {}'.format(e))
        sys.exit(1)
    except ValueError as e:
        click.echo(u'ERROR: Invalid payload format: {error}'.format(error=e))
        sys.exit(1)

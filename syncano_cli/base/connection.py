# -*- coding: utf-8 -*-
import sys
from ConfigParser import NoOptionError, NoSectionError

import click
import syncano
from syncano_cli.config import ACCOUNT_CONFIG, ACCOUNT_CONFIG_PATH


def create_connection(config):
    config = config or ACCOUNT_CONFIG_PATH
    ACCOUNT_CONFIG.read(config)
    api_key = ACCOUNT_CONFIG.get('DEFAULT', 'key')
    connection_dict = {
        'api_key': api_key,
    }
    instance_name = ACCOUNT_CONFIG.get('DEFAULT', 'instance_name', None)
    if instance_name:
        connection_dict['instance_name'] = instance_name
    return syncano.connect(**connection_dict)


def get_instance_name(config, instance_name):
    ACCOUNT_CONFIG.read(config)
    try:
        instance_name = instance_name or ACCOUNT_CONFIG.get('DEFAULT', 'instance_name')
    except (NoOptionError, NoSectionError):
        click.echo("ERROR: instance name not specified: nor default, nor as an option.")
        sys.exit(1)
    return instance_name

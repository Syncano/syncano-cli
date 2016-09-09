# -*- coding: utf-8 -*-
from ConfigParser import NoOptionError, NoSectionError

import syncano
from syncano.exceptions import SyncanoException
from syncano_cli.base.exceptions import BadCredentialsException, InstanceNotFoundException
from syncano_cli.config import ACCOUNT_CONFIG, ACCOUNT_CONFIG_PATH


def get_instance_name(config, instance_name):
    ACCOUNT_CONFIG.read(config)
    try:
        instance_name = instance_name or ACCOUNT_CONFIG.get('DEFAULT', 'instance_name')
    except (NoOptionError, NoSectionError):
        return None
    return instance_name


def create_connection(config, instance_name=None):
    config = config or ACCOUNT_CONFIG_PATH
    ACCOUNT_CONFIG.read(config)
    api_key = ACCOUNT_CONFIG.get('DEFAULT', 'key')
    connection_dict = {
        'api_key': api_key,
    }
    instance_name = get_instance_name(config, instance_name)
    if instance_name:
        connection_dict['instance_name'] = instance_name
    try:
        return syncano.connect(**connection_dict)
    except SyncanoException:
        raise BadCredentialsException()


def get_instance(config, instance_name, connection=None):
    config = config or ACCOUNT_CONFIG_PATH
    instance_name = get_instance_name(config, instance_name)

    connection = connection or create_connection(config, instance_name=instance_name)
    try:
        return connection.Instance.please.get(name=instance_name)
    except SyncanoException:
        raise InstanceNotFoundException(format_args=[instance_name])

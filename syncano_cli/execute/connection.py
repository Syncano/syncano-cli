# -*- coding: utf-8 -*-
import syncano
from syncano_cli.config import ACCOUNT_CONFIG, ACCOUNT_CONFIG_PATH


def create_instance_connection(config, instance):
    config = config or ACCOUNT_CONFIG_PATH
    ACCOUNT_CONFIG.read(config)
    api_key = ACCOUNT_CONFIG.get('DEFAULT', 'key')
    return syncano.connect(api_key=api_key, instance_name=instance).connection()

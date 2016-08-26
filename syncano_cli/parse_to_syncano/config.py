# -*- coding: utf-8 -*-

import os

from syncano_cli.config import ACCOUNT_CONFIG

CONFIG_VARIABLES_NAMES = ['PARSE_MASTER_KEY', 'PARSE_APPLICATION_ID',
                          'SYNCANO_ADMIN_API_KEY', 'SYNCANO_INSTANCE_NAME']

PARSE_APPLICATION_ID = os.getenv('PARSE_APPLICATION_ID', '')
PARSE_MASTER_KEY = os.getenv('PARSE_MASTER_KEY', '')

SYNCANO_INSTANCE_NAME = os.getenv('SYNCANO_INSTANCE_NAME', '')
SYNCANO_ADMIN_API_KEY = os.getenv('SYNCANO_ADMIN_API_KEY', '')

PARSE_PAGINATION_LIMIT = 1000  # the biggest value parse allows
SYNCANO_BATCH_SIZE = 30


def read_config(config_path):
    config = ACCOUNT_CONFIG

    read_ok = config.read(config_path)

    if not read_ok:
        config.add_section("P2S")
        config.set("P2S", "PARSE_APPLICATION_ID", PARSE_APPLICATION_ID)
        config.set("P2S", "PARSE_MASTER_KEY", PARSE_MASTER_KEY)
        config.set("P2S", "SYNCANO_INSTANCE_NAME", SYNCANO_INSTANCE_NAME)
        config.set("P2S", "SYNCANO_ADMIN_API_KEY", SYNCANO_ADMIN_API_KEY)

    return config

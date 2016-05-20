# -*- coding: utf-8 -*-

import os
from ConfigParser import ConfigParser

CONFIG_VARIABLES_NAMES = ['PARSE_MASTER_KEY', 'PARSE_APPLICATION_ID', 'SYNCANO_APIROOT',
                          'SYNCANO_ADMIN_API_KEY', 'SYNCANO_INSTANCE_NAME']

PARSE_APPLICATION_ID = os.getenv('P2S_PARSE_APPLICATION_ID', '')
PARSE_MASTER_KEY = os.getenv('P2S_PARSE_MASTER_KEY', '')

SYNCANO_INSTANCE_NAME = os.getenv('P2S_SYNCANO_INSTANCE_NAME', '')
SYNCANO_ADMIN_API_KEY = os.getenv('P2S_SYNCANO_ADMIN_API_KEY', '')
SYNCANO_APIROOT = os.getenv('P2S_SYNCANO_APIROOT', 'https://api.syncano.io')

PARSE_PAGINATION_LIMIT = 1000  # the biggest value parse allows

P2S_CONFIG_PATH = os.path.join(os.path.expanduser('~'), '.syncano')

config = ConfigParser()

read_ok = config.read(P2S_CONFIG_PATH)

if not read_ok:
    config.add_section("P2S")
    config.set("P2S", "PARSE_APPLICATION_ID", PARSE_APPLICATION_ID)
    config.set("P2S", "PARSE_MASTER_KEY", PARSE_MASTER_KEY)
    config.set("P2S", "SYNCANO_INSTANCE_NAME", SYNCANO_INSTANCE_NAME)
    config.set("P2S", "SYNCANO_ADMIN_API_KEY", SYNCANO_ADMIN_API_KEY)
    config.set("P2S", "SYNCANO_APIROOT", SYNCANO_APIROOT)

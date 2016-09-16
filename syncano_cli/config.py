# -*- coding: UTF=8 -*-

import os

import six

if six.PY2:
    from ConfigParser import ConfigParser
elif six.PY3:
    from configparser import ConfigParser
else:
    raise ImportError()

ACCOUNT_CONFIG_PATH = os.path.join(os.path.expanduser('~'), '.syncano')
ACCOUNT_CONFIG = ConfigParser()

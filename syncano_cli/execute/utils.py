# -*- coding: utf-8 -*-
from __future__ import print_function

import json

from syncano_cli.logger import get_logger

LOG = get_logger('syncano-execute')


def print_response(response):
    if hasattr(response, 'result'):
        if response.status == 'success':
            _print_result(response.result['stdout'])
        else:
            LOG.error(response.result['stderr'])
    else:
        _print_result(response)


def _print_result(result):
    try:
        if type(result) in [str, unicode]:
            output = json.loads(result)
        else:
            output = result
        print(json.dumps(output, indent=4, sort_keys=True))
    except ValueError:
        print(result)

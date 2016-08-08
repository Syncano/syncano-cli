# -*- coding: utf-8 -*-
from __future__ import print_function

import json


def print_response(response):
    if hasattr(response, 'result'):
        if response.status == 'success':
            _print_result(response.result['stdout'])
        else:
            print(response.result['stderr'])
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

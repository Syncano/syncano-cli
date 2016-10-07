# -*- coding: utf-8 -*-
import json

import six

from syncano_cli.base.command import BaseInstanceCommand
from syncano_cli.base.data_parser import parse_input_data


class ExecuteCommand(BaseInstanceCommand):

    def execute(self, script_endpoint_name, data):
        se = self.instance.script_endpoints.get(name=script_endpoint_name)
        data = parse_input_data(data)
        response = se.run(**data)
        self.print_response(response)

    def print_response(self, response):
        if hasattr(response, 'result'):
            if response.status == 'success':
                self._print_result(response.result['stdout'])
            else:
                self.output_formatter.write_line(response.result['stderr'])
        else:
            self._print_result(response)

    def _print_result(self, result):
        try:
            if isinstance(result, six.string_types):
                output = json.loads(result)
            else:
                output = result
            self.output_formatter.write_line(json.dumps(output, indent=4, sort_keys=True))
        except ValueError:
            self.output_formatter.write_line(result)

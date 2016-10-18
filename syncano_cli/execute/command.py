# -*- coding: utf-8 -*-
import json

import six
from syncano_cli.base.command import BaseCommand
from syncano_cli.base.data_parser import parse_input_data
from syncano_cli.base.options import BottomSpacedOpt, DefaultOpt, SpacedOpt, WarningOpt


class ExecuteCommand(BaseCommand):

    def execute(self, script_endpoint_name, data):
        se = self.instance.script_endpoints.get(name=script_endpoint_name)
        data = parse_input_data(data)
        response = se.run(**data)
        self.formatter.write('The result of the Script `{}` run is:'.format(script_endpoint_name), SpacedOpt())
        self.print_response(response)

    def print_response(self, response):
        if hasattr(response, 'result'):
            if response.status == 'success':
                self._print_result(response.result['stdout'])
            else:
                self.formatter.write(response.result['stderr'])
        else:
            self._print_result(response)

    def _print_result(self, result):
        try:
            if isinstance(result, six.string_types):
                output = json.loads(result)
            else:
                output = result
            self.formatter.write(json.dumps(output, indent=4, sort_keys=True), DefaultOpt(indent=2),
                                 BottomSpacedOpt(), WarningOpt())
        except ValueError:
            self.formatter.write(result, DefaultOpt(indent=2), BottomSpacedOpt())

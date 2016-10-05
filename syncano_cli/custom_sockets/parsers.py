# -*- coding: utf-8 -*-
import click
import six
from syncano_cli.custom_sockets.exceptions import BadConfigFormatException


class SocketConfigParser(object):

    PROMPT_FIELD = 'prompt'
    VALUE_FIELD = 'value'

    def __init__(self, socket_yml):
        self.config = socket_yml.get('config', [])

    def is_valid(self):
        valid = True
        for field_name in [self.PROMPT_FIELD, self.VALUE_FIELD]:
            valid &= self._is_valid(field_name)
        if not valid:
            raise BadConfigFormatException()
        return valid

    def _is_valid(self, field_name):
        if field_name in self.config and not len(self.config[field_name]):
            return False
        return True

    def ask_for_config(self):
        provided_config = {}
        for config_var_name, config_metadata in six.iteritems(self.config):
            if config_metadata.get('prompt'):
                default_value = config_metadata.get('value')
                config_var_value = click.prompt(self.get_prompt_str(config_var_name), default=default_value)
                provided_config[config_var_name] = config_var_value
            else:
                provided_config[config_var_name] = config_metadata.get('value')

        return provided_config

    @staticmethod
    def get_prompt_str(config_var_name):
        return 'Provide value for {}'.format(config_var_name)

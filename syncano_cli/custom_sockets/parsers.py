# -*- coding: utf-8 -*-
import click
import six
from syncano_cli.custom_sockets.exceptions import BadConfigFormatException


class SocketConfigParser(object):

    PROMPT_FIELD = 'prompt'
    CONSTANTS_FIELD = 'constants'

    def __init__(self, socket_yml):
        self.config = socket_yml.get('config', [])

    def is_valid(self):
        valid = True
        for field_name in [self.PROMPT_FIELD, self.CONSTANTS_FIELD]:
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
        if self.PROMPT_FIELD in self.config:
            for config_var_name, config_metadata in six.iteritems(self.config[self.PROMPT_FIELD]):
                config_var_value = click.prompt(self.get_prompt_str(config_var_name, config_metadata))
                provided_config[config_var_name] = config_var_value

        return provided_config

    @staticmethod
    def get_prompt_str(field_name, config_metadata):
        prompt_str = 'Provide value for {}'.format(field_name)
        if config_metadata.get('description'):
            prompt_str = '{} ({})'.format(prompt_str, config_metadata['description'])
        return prompt_str

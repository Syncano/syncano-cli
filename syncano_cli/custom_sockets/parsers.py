# -*- coding: utf-8 -*-

import sys

import click


class SocketConfigParser(object):

    def __init__(self, socket_yml):
        self.config = socket_yml.get('config', [])

    def is_valid(self):
        for config_var in self.config:
            if not config_var.get('name'):
                click.echo("ERROR: variable name should be provided in config.")
                sys.exit(1)

        return True

    def ask_for_config(self, instance_config):
        provided_config = {}
        for config_var in self.config:
            config_var_name = config_var['name']

            if config_var_name not in instance_config:
                config_var_value = click.prompt(self.get_prompt_str(config_var))
                provided_config[config_var_name] = config_var_value

        return provided_config

    @staticmethod
    def get_prompt_str(config_var):
        prompt_str = 'Provide value for {}'.format(config_var['name'])
        if config_var.get('description', None):
            prompt_str = '{} ({})'.format(prompt_str, config_var['description'])
        return prompt_str

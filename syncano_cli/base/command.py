# -*- coding: utf-8 -*-
import os

import six
from syncano_cli.base.connection import create_connection, get_instance
from syncano_cli.base.mixins import RegisterMixin
from syncano_cli.base.output_formatter import OutputFormatter
from syncano_cli.base.prompter import Prompter
from syncano_cli.config import ACCOUNT_CONFIG


class BaseCommand(RegisterMixin):

    output_formatter = OutputFormatter()
    prompter = Prompter()

    META_CONFIG = {
        'default': [
            {
                'name': 'key',
                'required': True,
                'info': ''
            },
            {
                'name': 'instance_name',
                'required': False,
                'info': 'You can setup it using following command: syncano instances default <instance_name>.'
            },
        ]
    }
    DEFAULT_SECTION = 'default'

    COMMAND_CONFIG = None
    COMMAND_SECTION = None
    COMMAND_CONFIG_PATH = None

    def has_setup(self, config_path):
        has_global = self.has_global_setup(config_path)
        has_command = self.has_command_setup(self.COMMAND_CONFIG_PATH)
        if has_global and has_command:
            return True

        if not has_global:
            self.output_formatter.write_space_line('Login or create an account in Syncano.',
                                                   color=self.output_formatter.color_schema.WARNING)
            email = self.prompter.prompt('email')
            password = self.prompter.prompt('password', hide_input=True)
            repeat_password = self.prompter.prompt('repeat password', hide_input=True)
            password = self.validate_password(password, repeat_password)
            self.do_login_or_register(email, password, config_path)

        if not has_command:
            self.setup_command_config(config_path)

        return False

    def has_command_setup(self, config_path):
        if not config_path:
            return True
        return False

    def setup_command_config(self, config_path):  # noqa;
        # override this in the child class;
        return True

    @classmethod
    def has_global_setup(cls, config_path):
        if os.path.isfile(config_path):
            with open(config_path, 'rt') as fp:
                ACCOUNT_CONFIG.read(fp)

            # check DEFAULT section;
            cls.check_section(ACCOUNT_CONFIG)
            return True

        return False

    @classmethod
    def check_section(cls, config_parser, section=None):
        section = section or cls.DEFAULT_SECTION
        if not config_parser.has_section(section):
            return False
        config = {}
        config.update(cls.META_CONFIG)
        config.update(cls.COMMAND_CONFIG or {})
        for config_name, config_meta in six.iteritems(config):
            var_name = config_meta['name']
            required = config_meta['required']
            if required and not config_parser.has_option(section, var_name):
                return False
            elif not required and not config_parser.has_option(section, var_name):
                cls.output_formatter.write_space_line(
                    'Missing "{}" in default config. {}'.format(var_name, config_meta['info']),
                    color=cls.output_formatter.color_schema.WARNING
                )

        return True

    def validate_password(self, password, repeat_password):
        while password != repeat_password:
            self.output_formatter.write_space_line('Password and repeat password are not the same. Please correct:',
                                                   color=self.output_formatter.color_schema.ERROR)
            password = self.prompter.prompt('password', hide_input=True)
            repeat_password = self.prompter.prompt('repeat password', hide_input=True)

        return password


class BaseInstanceCommand(BaseCommand):

    def set_instance(self, config_path, instance_name):
        self.instance = get_instance(config_path, instance_name)


class BaseConnectionCommand(BaseCommand):

    def set_connection(self, config_path):
        self.connection = create_connection(config_path)

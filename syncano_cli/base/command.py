# -*- coding: utf-8 -*-
import os

from syncano_cli.base.connection import ConnectionMixin
from syncano_cli.base.formatters import Formatter
from syncano_cli.base.mixins import RegisterMixin
from syncano_cli.base.options import SpacedOpt
from syncano_cli.base.prompter import Prompter
from syncano_cli.config import Config


class BaseCommand(ConnectionMixin, RegisterMixin):
    """
    Base command class. Provides utilities for register/loging (setup an account);
    Has a predefined class for prompting and format output nicely in the console;
    Stores also meta information about global config. Defines structures for command like config, eg.: hosting;
    """

    def __init__(self, config_path):
        self.config = Config(global_config_path=config_path)
        self.config.read_configs()
        self.connection = self.create_connection()
        self.setup()

    formatter = Formatter()
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
    DEFAULT_SECTION = 'DEFAULT'

    COMMAND_CONFIG = None
    COMMAND_SECTION = None
    COMMAND_CONFIG_PATH = None

    def setup(self):
        has_global = self.has_global_setup()
        has_command = self.has_command_setup(self.COMMAND_CONFIG_PATH)
        if has_global and has_command:
            return True

        if not has_global:
            self.formatter.write('Login or create an account in Syncano.', SpacedOpt())
            email = self.prompter.prompt('email')
            password = self.prompter.prompt('password', hide_input=True)
            repeat_password = self.prompter.prompt('repeat password', hide_input=True)
            password = self.validate_password(password, repeat_password)
            self.do_login_or_register(email, password)

        if not has_command:
            self.setup_command_config(self.COMMAND_CONFIG_PATH)

        return False

    def has_command_setup(self, config_path):
        if not config_path:
            return True
        return False

    def setup_command_config(self, config_path):  # noqa;
        """override this in the child class;"""

    def has_global_setup(self):

        if os.path.isfile(self.config.global_config_path):
            return self.check_section(self.config.global_config)

        return False

    @classmethod
    def check_section(cls, config_parser, section=None):
        section = section or cls.DEFAULT_SECTION

        if not config_parser.get(cls.DEFAULT_SECTION, 'key'):
            return False

        config_vars = []
        config_vars.extend(cls.META_CONFIG[cls.DEFAULT_SECTION.lower()])

        for config_meta in config_vars:
            var_name = config_meta['name']
            required = config_meta['required']
            if required and not config_parser.has_option(section, var_name):
                return False

        return True


class BaseInstanceCommand(BaseCommand):
    """Command for Instance based commands: fetch data from an instance."""
    def set_instance(self, instance_name):
        self._set_instance(instance_name)

    def _set_instance(self, instance_name):
        self.instance = self.get_instance(instance_name)

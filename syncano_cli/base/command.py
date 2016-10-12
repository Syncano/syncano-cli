# -*- coding: utf-8 -*-
import os

import six
from syncano_cli.base.connection import create_connection, get_instance
from syncano_cli.base.formatters import Formatter
from syncano_cli.base.mixins import RegisterMixin
from syncano_cli.base.options import SpacedOpt, WarningOpt
from syncano_cli.base.prompter import Prompter
from syncano_cli.config import ACCOUNT_CONFIG

if six.PY2:
    from ConfigParser import NoOptionError
elif six.PY3:
    from configparser import NoOptionError
else:
    raise ImportError()


class BaseCommand(RegisterMixin):
    """
    Base command class. Provides utilities for register/loging (setup an account);
    Has a predefined class for prompting and format output nicely in the console;
    Stores also meta information about global config. Defines structures for command like config, eg.: hosting;
    """

    def __init__(self, config_path):
        self.config_path = config_path
        self.connection = create_connection(config_path)

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

    def has_setup(self):
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
            self.do_login_or_register(email, password, self.config_path)

        if not has_command:
            self.setup_command_config(self.config_path)

        return False

    def has_command_setup(self, config_path):
        if not config_path:
            return True
        return False

    def setup_command_config(self, config_path):  # noqa;
        # override this in the child class;
        return True

    def has_global_setup(self):
        if os.path.isfile(self.config_path):
            ACCOUNT_CONFIG.read(self.config_path)
            return self.check_section(ACCOUNT_CONFIG)

        return False

    @classmethod
    def check_section(cls, config_parser, section=None):
        section = section or cls.DEFAULT_SECTION
        try:
            config_parser.get(cls.DEFAULT_SECTION, 'key')
        except NoOptionError:
            return False

        config_vars = []
        config_vars.extend(cls.META_CONFIG[cls.DEFAULT_SECTION.lower()])
        if cls.COMMAND_CONFIG:
            config_vars.extend(cls.COMMAND_CONFIG.get(cls.COMMAND_SECTION) or {})
        for config_meta in config_vars:
            var_name = config_meta['name']
            required = config_meta['required']
            if required and not config_parser.has_option(section, var_name):
                return False
            elif not required and not config_parser.has_option(section, var_name):
                cls.formatter.write(
                    'Missing "{}" in default config. {}'.format(var_name, config_meta['info']),
                    WarningOpt(), SpacedOpt()
                )

        return True


class BaseInstanceCommand(BaseCommand):
    """Command for Instance based commands: fetch data from an instance."""
    def set_instance(self, instance_name):
        self._set_instance(instance_name)

    def _set_instance(self, instance_name):
        self.instance = get_instance(self.config_path, instance_name)

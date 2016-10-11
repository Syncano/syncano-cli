# -*- coding: utf-8 -*-
import sys

import syncano
from syncano.exceptions import SyncanoRequestError
from syncano_cli.base.options import ErrorOpt, SpacedOpt, TopSpacedOpt
from syncano_cli.config import ACCOUNT_CONFIG
from syncano_cli.init.helpers import random_instance_name


class RegisterMixin(object):

    def do_login(self, email, password, config_path):
        connection = syncano.connect().connection()
        api_key = connection.authenticate(email=email, password=password)
        ACCOUNT_CONFIG.set('DEFAULT', 'key', api_key)
        with open(config_path, 'wt') as fp:
            ACCOUNT_CONFIG.write(fp)

    def do_register(self, exc, email, password, config_path):
        if exc.status_code == 401:
            if 'email' in exc.message:
                from syncano_cli.account.command import AccountCommands
                account_command = AccountCommands(config_path=config_path)
                account_command.register(email=email, password=password)
                self.output_formatter.write('Account created for email: {}'.format(email),
                                            TopSpacedOpt())
            elif 'password' in exc.message:
                self.output_formatter.write('Invalid login: you have provided wrong password.', ErrorOpt())
                sys.exit(1)

    def create_instance(self, instance_commands):
        instance_name = random_instance_name()
        return instance_commands.create(instance_name=instance_name)

    def do_login_or_register(self, email, password, config_path):
        try:
            self.do_login(email, password, config_path)
        except SyncanoRequestError as exc:
            self.do_register(exc, email, password, config_path)

        from syncano_cli.instance.command import InstanceCommands
        instance_commands = InstanceCommands(self.config_path)
        instances = [i for i in instance_commands.api_list()]
        instance_name = instances[0].name if instances else self.create_instance(instance_commands).name
        self.set_instance_as_default(config_path, instance_name, instance_commands)

    def set_instance_as_default(self, config_path, instance_name, instance_commands):
        self.output_formatter.write('Instance `{}` set as default.'.format(instance_name), TopSpacedOpt())
        instance_commands.set_default(instance_name=instance_name, config_path=config_path)

    def validate_password(self, password, repeat_password):
        while password != repeat_password:
            self.output_formatter.write('Password and repeat password are not the same. Please correct:', ErrorOpt(),
                                        SpacedOpt())
            password = self.prompter.prompt('password', hide_input=True)
            repeat_password = self.prompter.prompt('repeat password', hide_input=True)

        return password

# -*- coding: utf-8 -*-
import sys

import syncano
from syncano.exceptions import SyncanoRequestError
from syncano_cli.account.command import AccountCommands
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
                account_command = AccountCommands(config_path=config_path)
                account_command.register(email=email, password=password)
            elif 'password' in exc.message:
                self.output_formatter.write_space_line('Invalid login: you have provided wrong password.',
                                                       color=self.ourput_formatter.color_schema.ERROR)
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
        instance_commands = InstanceCommands()
        instance_commands.set_connection(config_path)
        instances = [i for i in instance_commands.api_list()]
        instance_name = instances[0].name if instances else self.create_instance(instance_commands).name
        self.set_instance_as_default(config_path, instance_name, instance_commands)

    def set_instance_as_default(self, config_path, instance_name, instance_commands):
        self.output_formatter.write_space_line('Instance `{}` set as default.'.format(instance_name), bottom=False)
        instance_commands.set_default(instance_name=instance_name, config_path=config_path)

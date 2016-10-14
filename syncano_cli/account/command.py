# -*- coding: utf-8 -*-

import syncano
from syncano_cli.base.command import BaseCommand
from syncano_cli.config import Config


class AccountCommands(BaseCommand):

    def __init__(self, config_path):
        self.config = Config(global_config_path=config_path)
        self.connection = syncano.connect()

    def register(self, email, password, first_name=None, last_name=None):
        api_key = self.connection.connection().register(
            email=email,
            password=password,
            first_name=first_name,
            last_name=last_name,
        )
        self.config.set_config('DEFAULT', 'key', api_key)
        self.config.write_config()

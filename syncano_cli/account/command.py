# -*- coding: utf-8 -*-

import syncano
from syncano_cli.config import ACCOUNT_CONFIG


class AccountCommands(object):

    def __init__(self, config_path):
        self.connection = syncano.connect()
        self.config_path = config_path

    def register(self, email, password, first_name, last_name, invitation_key):
        api_key = self.connection.connection().register(
            email=email,
            password=password,
            first_name=first_name,
            last_name=last_name,
            invitation_key=invitation_key
        )

        ACCOUNT_CONFIG.set('DEFAULT', 'api_key', api_key)
        with open(self.config_path, 'wb') as fp:
            ACCOUNT_CONFIG.write(fp)

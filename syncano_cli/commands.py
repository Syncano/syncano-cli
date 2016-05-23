# -*- coding: utf-8 -*-
import os
from getpass import getpass

import six
import syncano
from syncano.exceptions import SyncanoException
from syncano_cli.commands_base import CommandContainer
from syncano_cli.parse_to_syncano.commands import Configure, Parse  # noqa
from syncano_cli.sync.commands import Pull, Push  # noqa

COMMAND_NAMESPACE = 'toplevel'


class Login(six.with_metaclass(CommandContainer)):
    namespace = COMMAND_NAMESPACE

    @classmethod
    def run(cls, context):
        """
        Log in to syncano using email and password and store ACCOUNT_KEY
        in configuration file.
        """
        email = os.environ.get('SYNCANO_EMAIL', None)
        if email is None:
            email = raw_input("email: ")
        password = os.environ.get('SYNCANO_PASSWORD', None)
        if password is None:
            password = getpass("password: ").strip()
        connection = syncano.connect().connection()
        try:
            from syncano_cli.main import ACCOUNT_CONFIG
            ACCOUNT_KEY = connection.authenticate(email=email, password=password)
            ACCOUNT_CONFIG.set('DEFAULT', 'key', ACCOUNT_KEY)
            with open(context.config, 'wb') as fp:
                ACCOUNT_CONFIG.write(fp)
        except SyncanoException as error:
            print(error)

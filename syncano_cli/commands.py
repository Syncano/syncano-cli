# -*- coding: utf-8 -*-
import os
from getpass import getpass

import click
import syncano
from syncano.exceptions import SyncanoException
from syncano_cli.config import ACCOUNT_CONFIG_PATH


@click.group()
@click.pass_context
def top_level(context, config):
    pass


@top_level.command()
@click.pass_context
@click.option('--config', help=u'Account configuration file.')
def login(context, config):
    """
    Log in to syncano using email and password and store ACCOUNT_KEY
    in configuration file.
    """
    config = config or ACCOUNT_CONFIG_PATH
    context.obj['config'] = config
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
        with open(context.obj['config'], 'wb') as fp:
            ACCOUNT_CONFIG.write(fp)
    except SyncanoException as error:
        print(error)

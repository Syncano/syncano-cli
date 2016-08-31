# -*- coding: utf-8 -*-
import os
from getpass import getpass

import click
import syncano
from syncano.exceptions import SyncanoException
from syncano_cli.config import ACCOUNT_CONFIG, ACCOUNT_CONFIG_PATH


@click.group()
@click.pass_context
def top_level(context):
    pass


@top_level.command()
@click.pass_context
@click.option('--config', help=u'Account configuration file.')
@click.option('--instance-name', help=u'Default instance name.')
def login(context, config, instance_name):
    """
    Log in to syncano using email and password and store ACCOUNT_KEY
    in configuration file.
    """
    config = config or ACCOUNT_CONFIG_PATH
    context.obj['config'] = config
    email = os.environ.get('SYNCANO_EMAIL')
    if email is None:
        email = raw_input("email: ")
    password = os.environ.get('SYNCANO_PASSWORD')
    if password is None:
        password = getpass("password: ").strip()
    connection = syncano.connect().connection()
    try:
        ACCOUNT_KEY = connection.authenticate(email=email, password=password)
        ACCOUNT_CONFIG.set('DEFAULT', 'key', ACCOUNT_KEY)
        if instance_name:
            ACCOUNT_CONFIG.set('DEFAULT', 'instance_name', instance_name)
        with open(context.obj['config'], 'wb') as fp:
            ACCOUNT_CONFIG.write(fp)
        click.echo("INFO: Login successful.")
    except SyncanoException as error:
        print(error)

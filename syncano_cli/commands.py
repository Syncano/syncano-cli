# -*- coding: utf-8 -*-
import os

import click
import syncano
from syncano.exceptions import SyncanoException
from syncano_cli.base.command import BaseCommand
from syncano_cli.base.exceptions import BadCredentialsException
from syncano_cli.base.options import SpacedOpt
from syncano_cli.config import ACCOUNT_CONFIG, ACCOUNT_CONFIG_PATH


@click.group()
def top_level():
    pass


@top_level.command()
@click.pass_context
@click.option('--config', help=u'Account configuration file.')
@click.option('--instance-name', help=u'Default instance name.')
def login(context, config, instance_name):
    """
    Log in to syncano using email and password.
    """
    config = config or ACCOUNT_CONFIG_PATH
    context.obj['config'] = config
    command = BaseCommand(config)
    command.formatter.write('Login to your Syncano account. '
                            'This action will override your Syncano API key in global CLI config.', SpacedOpt())
    email = os.environ.get('SYNCANO_EMAIL') or command.prompter.prompt("email")
    password = os.environ.get('SYNCANO_PASSWORD') or command.prompter.prompt("password", hide_input=True).strip()
    connection = syncano.connect().connection()

    try:
        ACCOUNT_KEY = connection.authenticate(email=email, password=password)
        ACCOUNT_CONFIG.set('DEFAULT', 'key', ACCOUNT_KEY)
        if instance_name:
            ACCOUNT_CONFIG.set('DEFAULT', 'instance_name', instance_name)
        with open(context.obj['config'], 'wt') as fp:
            ACCOUNT_CONFIG.write(fp)
        command.formatter.write("Login successful.", SpacedOpt())
    except SyncanoException:
        raise BadCredentialsException()

# -*- coding: utf-8 -*-
import os

import click
import syncano
from syncano.exceptions import SyncanoException
from syncano_cli.base.command import BaseCommand
from syncano_cli.base.exceptions import BadCredentialsException
from syncano_cli.base.options import SpacedOpt


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
    context.obj['config'] = config
    command = BaseCommand(config)
    command.formatter.write('Login to your Syncano account. '
                            'This action will override your Syncano API key in global CLI config.', SpacedOpt())
    email = os.environ.get('SYNCANO_EMAIL') or command.prompter.prompt("email")
    password = os.environ.get('SYNCANO_PASSWORD') or command.prompter.prompt("password", hide_input=True).strip()
    connection = syncano.connect().connection()

    try:
        ACCOUNT_KEY = connection.authenticate(email=email, password=password)
        command.config.set_config('DEFAULT', 'key', ACCOUNT_KEY)
        if instance_name:
            command.config.set_config('DEFAULT', 'instance_name', instance_name)
        command.config.write_config()
        command.formatter.write("Login successful.", SpacedOpt())
    except SyncanoException:
        raise BadCredentialsException()

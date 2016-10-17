# -*- coding: utf-8 -*-

import click
from syncano_cli.base.command import BaseCommand
from syncano_cli.base.options import SpacedOpt


@click.group()
def top_level():
    pass


@top_level.command()
@click.option('--config', help=u'Account configuration file.')
@click.option('--instance-name', help=u'Default instance name.')
def login(config, instance_name):
    """
    Log in to syncano using email and password.
    """
    command = BaseCommand(config)
    if instance_name:
        command.config.set_config('DEFAULT', 'instance_name', instance_name)
        command.config.write_config()

    email = command.config.get_config('DEFAULT', 'email')
    if not email:
        command.formatter.write('Already logged in.', SpacedOpt())
    else:
        command.formatter.write('Already logged in as: {}.'.format(email), SpacedOpt())

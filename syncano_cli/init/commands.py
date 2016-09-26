# -*- coding: utf-8 -*-
import click
from syncano_cli.account.command import AccountCommands
from syncano_cli.base.connection import create_connection
from syncano_cli.config import ACCOUNT_CONFIG_PATH
from syncano_cli.init.helpers import random_instance_name
from syncano_cli.instance.command import InstanceCommands


@click.group()
def top_init():
    pass


@top_init.command()
@click.pass_context
@click.option('--config', help=u'Account configuration file.', default=ACCOUNT_CONFIG_PATH)
@click.option('--email', prompt=True)
@click.option('--password', prompt=True, hide_input=True, confirmation_prompt=True)
def init(ctx, config, email, password):
    """Register new user and create first instance."""
    # register new account;
    account_command = AccountCommands(config_path=config)
    account_command.register(
        email=email,
        password=password,
    )

    # register sum up show;
    click.echo()
    click.echo('Account created for email: {}'.format(email))

    # create instance;
    connection = create_connection(config)
    instance_commands = InstanceCommands(connection)
    instance_name = random_instance_name()
    instance_commands.create(instance_name=instance_name)
    instance_commands.set_default(instance_name=instance_name, config_path=config)

    # instace sum up show;
    click.echo()
    click.echo('Instance `{}` created.'.format(instance_name))

    # show instructions;
    click.echo()
    click.echo(ctx.parent.get_help())

# -*- coding: utf-8 -*-

import sys

import click
from syncano_cli.base.connection import create_connection, get_instance_name
from syncano_cli.config import ACCOUNT_CONFIG_PATH
from syncano_cli.config_commands.command import ConfigCommand


@click.group()
def top_config():
    pass


@top_config.group(invoke_without_command=True)
@click.pass_context
@click.option('--config', help=u'Account configuration file.')
@click.option('--instance-name', help=u'Instance name.')
def config(ctx, config, instance_name):
    config = config or ACCOUNT_CONFIG_PATH
    instance_name = get_instance_name(config, instance_name)

    try:
        connection = create_connection(config)
        instance = connection.Instance.please.get(name=instance_name)
        config_command = ConfigCommand(instance=instance)
        ctx.obj['config_command'] = config_command
        if ctx.invoked_subcommand is None:
            config_command.config_show()

    except Exception as e:
        click.echo(u'ERROR: {}'.format(e))
        sys.exit(1)


@config.command()
@click.pass_context
@click.argument('name')
@click.argument('value')
def add(ctx, name, value):

    config_command = ctx.obj['config_command']

    try:
        config_command.add(name, value)

    except Exception as e:
        click.echo(u'ERROR: {}'.format(e))
        sys.exit(1)


@config.command()
@click.pass_context
@click.argument('name')
@click.argument('value')
def modify(ctx, name, value):

    config_command = ctx.obj['config_command']

    try:
        config_command.modify(name, value)

    except Exception as e:
        click.echo(u'ERROR: {}'.format(e))
        sys.exit(1)


@config.command()
@click.pass_context
@click.argument('name')
def delete(ctx, name):

    config_command = ctx.obj['config_command']

    try:
        config_command.delete(name)

    except Exception as e:
        click.echo(u'ERROR: {}'.format(e))
        sys.exit(1)

# -*- coding: utf-8 -*-

import click
from syncano_cli.base.connection import get_instance
from syncano_cli.config_commands.command import ConfigCommand


@click.group()
def top_config():
    pass


@top_config.group(invoke_without_command=True)
@click.pass_context
@click.option('--config', help=u'Account configuration file.')
@click.option('--instance-name', help=u'Instance name.')
def config(ctx, config, instance_name):
    """Allow to manage global instance config."""
    instance = get_instance(config, instance_name)
    config_command = ConfigCommand(instance=instance)
    ctx.obj['config_command'] = config_command
    if ctx.invoked_subcommand is None:
        config_command.config_show()


@config.command()
@click.pass_context
@click.argument('name')
@click.argument('value')
def add(ctx, name, value):
    """Add config variable to global instance config."""
    config_command = ctx.obj['config_command']
    config_command.add(name, value)


@config.command()
@click.pass_context
@click.argument('name')
@click.argument('value')
def modify(ctx, name, value):
    """Modify config value in global instance config."""
    config_command = ctx.obj['config_command']
    config_command.modify(name, value)


@config.command()
@click.pass_context
@click.argument('name')
def delete(ctx, name):
    """Removes config value from global instance config."""
    config_command = ctx.obj['config_command']
    config_command.delete(name)

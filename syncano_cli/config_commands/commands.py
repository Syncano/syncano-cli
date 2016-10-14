# -*- coding: utf-8 -*-

import click
from syncano_cli.config_commands.command import ConfigCommand


@click.group()
def top_config():
    pass


@top_config.group(invoke_without_command=True)
@click.pass_context
@click.option('--config', help=u'Account configuration file.')
@click.option('--instance-name', help=u'Instance name.')
def config(ctx, config, instance_name):
    """Allow to manage global Instance config."""

    config_command = ConfigCommand(config)
    config_command.set_instance(instance_name)
    ctx.obj['config_command'] = config_command
    if ctx.invoked_subcommand is None:
        config_command.config_show()


@config.command()
@click.pass_context
@click.argument('name')
@click.argument('value')
def add(ctx, name, value):
    """Add config variable to global Instance config."""
    config_command = ctx.obj['config_command']
    config_command.add(name, value)


@config.command()
@click.pass_context
@click.argument('name')
@click.argument('value')
def modify(ctx, name, value):
    """Modify config value in global Instance config."""
    config_command = ctx.obj['config_command']
    config_command.modify(name, value)


@config.command()
@click.pass_context
@click.argument('name')
def delete(ctx, name):
    """Removes config value from global Instance config."""
    config_command = ctx.obj['config_command']
    config_command.delete(name)

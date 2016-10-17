# -*- coding: utf-8 -*-

import sys

import click
from syncano_cli.base.options import ErrorOpt, SpacedOpt
from syncano_cli.instance.command import InstanceCommands
from syncano_cli.instance.exceptions import InstanceNameMismatchException, InstancesNotFoundException


@click.group()
def top_instance():
    pass


@top_instance.group()
@click.pass_context
@click.option('--config', help=u'Account configuration file.')
def instances(ctx, config):
    """
    Manage your Instances. Instance is an equivalent of a project or a set of data.
    It contains information about Sockets, Data Classes, Data Objects and more.
    You can own and/or belong to multiple Instances.
    """
    instance_commands = InstanceCommands(config)
    ctx.obj['instance_commands'] = instance_commands
    ctx.obj['config'] = config


@instances.command()
@click.pass_context
def list(ctx):
    """Display a list with defined Instances in Syncano. List displays only name and description."""
    instance_commands = ctx.obj['instance_commands']
    syncano_instances = instance_commands.list()
    if not syncano_instances:
        raise InstancesNotFoundException()
    instance_commands.display_list(syncano_instances)


@instances.command()
@click.pass_context
@click.argument('instance_name', required=False)
def details(ctx, instance_name):
    """Display Syncano Instance details."""
    instance_commands = ctx.obj['instance_commands']
    instance_name = instance_commands.get_instance_name(instance_name)  # default one if no provided;
    ctx.obj['instance_commands'].details(instance_name)


@instances.command()
@click.pass_context
@click.argument('instance_name', required=False)
def delete(ctx, instance_name):
    """Delete the Instance. Command will prompt you for permission."""
    instance_commands = ctx.obj['instance_commands']
    instance_name = instance_commands.get_instance_name(instance_name)  # default one if no provided;
    confirmed_name = instance_commands.prompter.prompt('Are you sure that you want to delete '
                                                       'Instance {}? Type Instance name again'.format(instance_name),
                                                       default='', show_default=False)
    if not confirmed_name:
        instance_commands.formatter.write('Aborted!', ErrorOpt(), SpacedOpt())
        sys.exit(1)
    if confirmed_name == instance_name:
        instance_commands.delete(instance_name)
    else:
        raise InstanceNameMismatchException()


@instances.command()
@click.pass_context
@click.argument('instance_name')
def default(ctx, instance_name):
    """Set the specified Instance name as default in CLI.
    This name will be used as default one when running commands."""
    ctx.obj['instance_commands'].set_default(instance_name, config_path=ctx.obj['config'])
    click.echo("INFO: Instance `{}` set as default.".format(instance_name))


@instances.command()
@click.pass_context
@click.argument('instance_name')
@click.option('--description')
def create(ctx, instance_name, description):
    """Create new Instance."""
    ctx.obj['instance_commands'].create(instance_name, description, show_default=True)

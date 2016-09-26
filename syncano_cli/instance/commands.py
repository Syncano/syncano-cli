# -*- coding: utf-8 -*-

import click
from syncano_cli.base.connection import create_connection, get_instance_name
from syncano_cli.config import ACCOUNT_CONFIG_PATH
from syncano_cli.instance.command import InstanceCommands
from syncano_cli.instance.exceptions import InstanceNameMismatchException, InstancesNotFoundException


@click.group()
def top_instance():
    pass


@top_instance.group()
@click.pass_context
@click.option('--config', help=u'Account configuration file.')
@click.option('--instance-name', help=u'Instance name.')
def instances(ctx, config, instance_name):
    """
    Manage your Instances. Instance is an equivalent of a project or a set of data.
    It contains information about Sockets, Data Classes, Data Objects and more.
    You can own and/or belong to multiple Instances.
    """
    connection = create_connection(config, instance_name)
    instance_commands = InstanceCommands(connection)
    ctx.obj['instance_commands'] = instance_commands
    ctx.obj['config'] = config or ACCOUNT_CONFIG_PATH


@instances.command()
@click.pass_context
def list(ctx):
    syncano_instances = ctx.obj['instance_commands'].list()
    if not syncano_instances:
        raise InstancesNotFoundException()
    click.echo(syncano_instances)


@instances.command()
@click.pass_context
@click.argument('instance_name', required=False)
def details(ctx, instance_name):
    instance_name = get_instance_name(ctx.obj['config'], instance_name)  # default one if no provided;
    instance_details = ctx.obj['instance_commands'].details(instance_name)
    click.echo(instance_details)


@instances.command()
@click.pass_context
@click.argument('instance_name', required=False)
def delete(ctx, instance_name):
    instance_name = get_instance_name(ctx.obj['config'], instance_name)  # default one if no provided;
    confirmed_name = click.prompt('Are you sure that you want to delete '
                                  'Instance {}? Type instance name again'.format(instance_name))
    if confirmed_name == instance_name:
        ctx.obj['instance_commands'].delete(instance_name)
    else:
        raise InstanceNameMismatchException()
    click.echo("INFO: Instance `{}` deleted.".format(instance_name))


@instances.command()
@click.pass_context
@click.argument('instance_name')
def default(ctx, instance_name):
    ctx.obj['instance_commands'].set_default(instance_name, config_path=ctx.obj['config'])
    click.echo("INFO: Instance `{}` set as default.".format(instance_name))


@instances.command()
@click.pass_context
@click.argument('instance_name')
@click.option('--description')
def create(ctx, instance_name, description):
    ctx.obj['instance_commands'].create(instance_name, description)
    click.echo("INFO: Instance `{}` created.".format(instance_name))

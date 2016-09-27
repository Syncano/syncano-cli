# -*- coding: utf-8 -*-

import click
from syncano_cli.base.connection import get_instance
from syncano_cli.base.data_parser import parse_input_data
from syncano_cli.custom_sockets.command import SocketCommand
from syncano_cli.custom_sockets.exceptions import MissingRequestDataException, SocketNameMissingException


@click.group()
def top_sockets():
    pass


@top_sockets.group()
@click.pass_context
@click.option('--config', help=u'Account configuration file.')
@click.option('--instance-name', help=u'Instance name.')
def sockets(ctx, config, instance_name):
    """
    Create and manage custom sockets.
    """
    instance = get_instance(config, instance_name)
    socket_command = SocketCommand(instance=instance)
    ctx.obj['socket_command'] = socket_command


@sockets.group(invoke_without_command=True)
@click.pass_context
def list(ctx):
    socket_command = ctx.obj['socket_command']
    if ctx.invoked_subcommand is None:
        socket_command.list()


@list.command()
@click.pass_context
def endpoints(ctx):
    socket_command = ctx.obj['socket_command']
    socket_command.list_endpoints()


@sockets.command()
@click.pass_context
@click.argument('source')
@click.option('--name', help='A socket name when installed from url.')
def install(ctx, source, name):
    socket_command = ctx.obj['socket_command']

    if 'http' in source:
        if not name:
            raise SocketNameMissingException()
        socket_command.install_from_url(url_path=source, name=name)
    else:
        socket_command.install_from_dir(dir_path=source)


@sockets.command()
@click.pass_context
@click.argument('socket_name')
def details(ctx, socket_name):
    socket_command = ctx.obj['socket_command']
    socket_command.details(socket_name=socket_name)


@sockets.command()
@click.pass_context
@click.argument('socket_name')
def config(ctx, socket_name):
    socket_command = ctx.obj['socket_command']
    socket_command.config(socket_name=socket_name)


@sockets.command()
@click.pass_context
@click.argument('socket_name')
def delete(ctx, socket_name):
    socket_command = ctx.obj['socket_command']
    socket_command.delete(socket_name=socket_name)


@sockets.command()
@click.pass_context
@click.argument('output_dir')
@click.option('--socket', help=u'Socket name from which the template should be created.')
def template(ctx, output_dir, socket):

    socket_command = ctx.obj['socket_command']

    if socket:
        socket_command.create_template(socket_name=socket, destination=output_dir)
    else:
        socket_command.create_template_from_local_template(destination=output_dir)


@sockets.command()
@click.pass_context
@click.argument('endpoint_name')
@click.argument('method', default=u'GET')
@click.option('-d', '--data', help=u'A data to be sent as payload: key=value', multiple=True)
def run(ctx, endpoint_name, method, data):
    socket_command = ctx.obj['socket_command']

    if method in ['POST', 'PUT', 'PATCH'] and not data:
        raise MissingRequestDataException(format_args=[method])

    data = parse_input_data(data)

    results = socket_command.run(endpoint_name, method=method, data=data)
    click.echo("{}".format(results))

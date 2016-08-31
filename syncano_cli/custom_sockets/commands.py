# -*- coding: utf-8 -*-
import json
import sys

import click
from syncano_cli.base.connection import create_connection, get_instance_name
from syncano_cli.config import ACCOUNT_CONFIG_PATH
from syncano_cli.custom_sockets.command import SocketCommand


@click.group()
def top_sockets():
    pass


@top_sockets.group()
@click.pass_context
@click.option('--config', help=u'Account configuration file.')
@click.option('--instance-name', help=u'Instance name.')
def sockets(ctx, config, instance_name):
    """
    Allow to create a custom socket.
    """
    config = config or ACCOUNT_CONFIG_PATH
    instance_name = get_instance_name(config, instance_name)
    try:
        connection = create_connection(config)
        instance = connection.Instance.please.get(name=instance_name)
        socket_command = SocketCommand(instance=instance)
        ctx.obj['socket_command'] = socket_command

    except Exception as e:
        click.echo(u'ERROR: {}'.format(e))
        sys.exit(1)


@sockets.group(invoke_without_command=True)
@click.pass_context
def list(ctx):
    socket_command = ctx.obj['socket_command']

    if ctx.invoked_subcommand is None:
        try:
            socket_command.list()

        except Exception as e:
            click.echo(u'ERROR: {}'.format(e))
            sys.exit(1)


@list.command()
@click.pass_context
def endpoints(ctx):
    socket_command = ctx.obj['socket_command']
    try:
        socket_command.list_endpoints()

    except Exception as e:
        click.echo(u'ERROR: {}'.format(e))
        sys.exit(1)


@sockets.command()
@click.pass_context
@click.argument('source')
@click.option('--name', help='A socket name when installed from url.')
def install(ctx, source, name):
    socket_command = ctx.obj['socket_command']

    try:
        if 'http' in source:
            if not name:
                click.echo('ERROR: name should be specified: --name')
                sys.exit(1)
            socket_command.install_from_url(url_path=source, name=name)

        else:
            socket_command.install_from_dir(dir_path=source)

    except Exception as e:
        click.echo(u'ERROR: {}'.format(e))
        sys.exit(1)


@sockets.command()
@click.pass_context
@click.argument('socket_name')
def details(ctx, socket_name):
    socket_command = ctx.obj['socket_command']

    try:
        socket_command.details(socket_name=socket_name)

    except Exception as e:
        click.echo(u'ERROR: {}'.format(e))
        sys.exit(1)


@sockets.command()
@click.pass_context
@click.argument('socket_name')
def delete(ctx, socket_name):
    socket_command = ctx.obj['socket_command']

    try:
        socket_command.delete(socket_name=socket_name)

    except Exception as e:
        click.echo(u'ERROR: {}'.format(e))
        sys.exit(1)


@sockets.command()
@click.pass_context
@click.argument('output_dir')
@click.option('--socket', help=u'Socket name from which the template should be created.')
def template(ctx, output_dir, socket):

    socket_command = ctx.obj['socket_command']

    try:
        if socket:
            socket_command.create_template(socket_name=socket, destination=output_dir)

        else:
            socket_command.create_template_from_local_template(destination=output_dir)

    except Exception as e:
        click.echo(u'ERROR: {}'.format(e))
        sys.exit(1)


@sockets.command()
@click.pass_context
@click.argument('endpoint_name')
@click.argument('method', default='GET')
@click.option('--data', help='A JSON formatted data')
def run(ctx, endpoint_name, method, data):
    socket_command = ctx.obj['socket_command']

    if method in ['POST', 'PUT', 'PATCH'] and not data:
        click.echo('ERROR: --data option should be provided when metho {} is used'.format(method))
        sys.exit(1)

    try:
        try:
            data = json.loads(data or '{}')
        except (ValueError, TypeError) as e:
            click.echo('ERROR: invalid JSON data. Parse error.')
            sys.exit(1)

        results = socket_command.run(endpoint_name, method=method, data=data)
        click.echo("{}".format(results))

    except Exception as e:
        click.echo(u'ERROR: {}'.format(e))
        sys.exit(1)

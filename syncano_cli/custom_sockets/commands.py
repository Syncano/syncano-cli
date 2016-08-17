# -*- coding: utf-8 -*-
import sys

import click
from syncano_cli.base.connection import create_connection
from syncano_cli.config import ACCOUNT_CONFIG_PATH
from syncano_cli.custom_sockets.parser import SocketParser


@click.group()
def top_sockets():
    pass


@top_sockets.group()
@click.pass_context
@click.option('--config', help=u'Account configuration file.')
@click.argument('instance_name', envvar='SYNCANO_INSTANCE')
def sockets(ctx, config, instance_name, **kwargs):
    """
    Allow to create a custom socket.
    """

    config = config or ACCOUNT_CONFIG_PATH
    try:
        connection = create_connection(config)
        instance = connection.Instance.please.get(name=instance_name)
        socket_parser = SocketParser(instance=instance)
        ctx.obj['socket_parser'] = socket_parser

    except Exception as e:
        click.echo(u'ERROR: {}'.format(e))
        sys.exit(1)


@sockets.command()
@click.pass_context
@click.option('--sockets', is_flag=True, help=u'List all defined custom sockets.')
@click.option('--endpoints', is_flag=True, help=u'List all defined endpoints.')
def list(ctx, sockets, endpoints):
    socket_parser = ctx.obj['socket_parser']
    if not sockets and not endpoints:
        click.echo('ERROR: specify on of the available flags: --sockets, --endpoints')

    try:
        if sockets:
            socket_parser.list()
        if endpoints:
            socket_parser.list_endpoints()

    except Exception as e:
        click.echo(u'ERROR: {}'.format(e))
        sys.exit(1)


@sockets.command()
@click.pass_context
@click.option('--dir', help=u'Directory path to read socket definition.')
@click.option('--url', help=u'An url path to the repository: eg.: github.')
def publish(ctx, **kwargs):
    socket_parser = ctx.obj['socket_parser']
    directory = kwargs.get('dir')
    url = kwargs.get('url')

    if not directory and not url:
        click.echo('ERROR: specify on of the available flags: --dir, --url')

    try:
        if directory:
            socket_parser.publish_from_dir(directory)

        if url:
            socket_parser.publish_from_url(url)

    except Exception as e:
        click.echo(u'ERROR: {}'.format(e))
        sys.exit(1)


@sockets.command()
@click.pass_context
@click.option('--details', help=u'Display details of the custom socket.')
@click.option('--delete', help=u'Deletes the custom socket.')
@click.option('--template', help=u'Create the template for custom socket creation. Provide output path.')
def socket(ctx, details, delete, template):
    socket_parser = ctx.obj['socket_parser']

    try:
        if details:
            socket_parser.details(socket_name=details)

        if delete:
            socket_parser.delete(socket_name=delete)

        if template:
            socket_parser.create_template(destination=template)

    except Exception as e:
        click.echo(u'ERROR: {}'.format(e))
        sys.exit(1)

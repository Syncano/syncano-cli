# -*- coding: utf-8 -*-

import click
from syncano_cli.base.data_parser import parse_input_data
from syncano_cli.base.options import SpacedOpt, WarningOpt
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
    """Create and manage Sockets."""
    socket_command = SocketCommand(config)
    socket_command.set_instance(instance_name)
    ctx.obj['socket_command'] = socket_command


@sockets.group(invoke_without_command=True)
@click.pass_context
def list(ctx):
    """List all defined sockets in Syncano."""
    socket_command = ctx.obj['socket_command']
    if ctx.invoked_subcommand is None:
        socket_command.list()


@list.command()
@click.pass_context
def endpoints(ctx):
    """List all defined Endpoints in Sockets."""
    socket_command = ctx.obj['socket_command']
    socket_command.list_endpoints()


@sockets.command()
@click.pass_context
@click.argument('source')
@click.option('--name', help='A socket name when installed from url.')
def install(ctx, source, name):
    """Install the Sockets. Can be installed from directory or from an url."""
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
    """Displays Socket details."""
    socket_command = ctx.obj['socket_command']
    socket_command.details(socket_name=socket_name)


@sockets.command()
@click.pass_context
@click.argument('socket_name')
def recheck(ctx, socket_name):
    """Allow to recheck socket."""
    socket_command = ctx.obj['socket_command']
    socket_command.formatter.write('Rechecking socket. See `syncano sockets details {}` in few seconds.'.format(
        socket_name
    ), SpacedOpt())
    socket_command.recheck(socket_name=socket_name)


@sockets.command()
@click.pass_context
@click.argument('socket_name')
def config(ctx, socket_name):
    """Display config for specified Sockets."""
    socket_command = ctx.obj['socket_command']
    socket_command.get_config(socket_name=socket_name)


@sockets.command()
@click.pass_context
@click.argument('socket_name')
def delete(ctx, socket_name):
    """Delete the specified Sockets."""
    socket_command = ctx.obj['socket_command']
    socket_command.delete(socket_name=socket_name)


@sockets.command()
@click.pass_context
@click.argument('output_dir')
@click.option('--socket', help=u'Socket name from which the template should be created.')
def template(ctx, output_dir, socket):
    """Creates a new template (local) from the
    Sockets that already exists in Syncano or has a local definition."""
    socket_command = ctx.obj['socket_command']

    if socket:
        socket_command.create_template(socket_name=socket, destination=output_dir)
    else:
        socket_command.create_template_from_local_template(destination=output_dir)
    socket_command.formatter.write('Template created in `{}`'.format(output_dir), SpacedOpt())


@sockets.command()
@click.pass_context
@click.argument('endpoint_name')
@click.argument('method', default=u'GET')
@click.option('-d', '--data', help=u'A data to be sent as payload: key=value', multiple=True)
def run(ctx, endpoint_name, method, data):
    """Run Endpoint and shows the output. Note that full name of an Endpoint consist of
    Sockets name and Endpoint name: <custom_socket_name>/<endpoint_name>."""
    socket_command = ctx.obj['socket_command']

    if method in ['POST', 'PUT', 'PATCH'] and not data:
        raise MissingRequestDataException(format_args=[method])

    data = parse_input_data(data)

    results = socket_command.run(endpoint_name, method=method, data=data)
    socket_command.formatter.write('Result for endpoint `{}`:'.format(endpoint_name), SpacedOpt(), WarningOpt())
    socket_command.formatter.write_lines("{}".format(results).splitlines())
    socket_command.formatter.empty_line()

# -*- coding: utf-8 -*-
import sys

import click
from syncano_cli.base.connection import create_connection, get_instance_name
from syncano_cli.config import ACCOUNT_CONFIG_PATH
from syncano_cli.hosting.command import HostingCommands
from syncano_cli.hosting.validators import validate_domain, validate_publish


@click.group()
def top_hosting():
    pass


@top_hosting.group()
@click.pass_context
@click.option('--config', help=u'Account configuration file.')
@click.option('--instance-name', help=u'Instance name.')
def hosting(ctx, config, instance_name):
    """
    Handle hosting and hosting files. Allow to publish static pages to the Syncano Hosting.
    """

    config = config or ACCOUNT_CONFIG_PATH
    instance_name = get_instance_name(config, instance_name)

    try:
        connection = create_connection(config)
        instance = connection.Instance.please.get(name=instance_name)

        hosting_commands = HostingCommands(instance)
        ctx.obj['hosting_commands'] = hosting_commands

    except Exception as e:
        click.echo(u'ERROR: {}'.format(e))
        sys.exit(1)


@hosting.command()
@click.pass_context
@click.argument('directory')
def publish(ctx, directory):

    validate_publish(directory)
    domain = validate_domain()  # prepared for user defined domains;

    hosting_commands = ctx.obj['hosting_commands']
    try:
        hosting_commands.publish(domain=domain, base_dir=directory)
    except Exception as e:
        click.echo(u'ERROR: {}'.format(e))
        sys.exit(1)


@hosting.command()
@click.pass_context
def unpublish(ctx):
    domain = validate_domain()
    hosting_commands = ctx.obj['hosting_commands']
    try:
        hosting_commands.unpublish(domain=domain)
    except Exception as e:
        click.echo(u'ERROR: {}'.format(e))
        sys.exit(1)


@hosting.command()
@click.pass_context
def list(ctx):
    hosting_commands = ctx.obj['hosting_commands']
    domain = validate_domain()
    try:
        hosting_commands.print_hosting_files(
            hosting_files=hosting_commands.list_hosting_files(domain)
        )
    except Exception as e:
        click.echo(u'ERROR: {}'.format(e))
        sys.exit(1)


@hosting.command()
@click.pass_context
@click.argument('path', required=False)
def delete(ctx, path):
    domain = validate_domain()
    hosting_commands = ctx.obj['hosting_commands']
    if not path:
        if click.confirm('Do you want to remove whole hosting?'):
            try:
                hosting_commands.delete_hosting(domain=domain, path=path)
            except Exception as e:
                click.echo(u'ERROR: {}'.format(e))
                sys.exit(1)
        else:
            click.echo("INFO: Deleting aborted.")
    else:
        try:
            hosting_commands.delete_path(domain=domain, path=path)
        except Exception as e:
            click.echo(u'ERROR: {}'.format(e))
            sys.exit(1)


@hosting.command()
@click.pass_context
@click.argument('path')
@click.argument('file')
def update(ctx, path, file):
    domain = validate_domain()
    hosting_commands = ctx.obj['hosting_commands']
    try:
        hosting_commands.update_single_file(domain=domain, path=path, file=file)
    except Exception as e:
        click.echo(u'ERROR: {}'.format(e))
        sys.exit(1)

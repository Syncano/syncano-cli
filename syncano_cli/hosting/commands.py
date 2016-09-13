# -*- coding: utf-8 -*-
import click
from click import Abort
from syncano_cli.base.connection import get_instance
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
    instance = get_instance(config, instance_name)
    hosting_commands = HostingCommands(instance)
    ctx.obj['hosting_commands'] = hosting_commands


@hosting.command()
@click.pass_context
@click.argument('directory')
def publish(ctx, directory):

    validate_publish(directory)
    domain = validate_domain()  # prepared for user defined domains;
    ctx.obj['hosting_commands'].publish(domain=domain, base_dir=directory)


@hosting.command()
@click.pass_context
def unpublish(ctx):
    domain = validate_domain()
    ctx.obj['hosting_commands'].unpublish(domain=domain)


@hosting.command()
@click.pass_context
def list(ctx):
    domain = validate_domain()
    hosting_commands = ctx.obj['hosting_commands']
    hosting_commands.print_hosting_files(
        hosting_files=hosting_commands.list_hosting_files(domain)
    )


@hosting.command()
@click.pass_context
@click.argument('path', required=False)
def delete(ctx, path):
    domain = validate_domain()
    hosting_commands = ctx.obj['hosting_commands']
    if not path:
        if click.confirm('Do you want to remove whole hosting?'):
            hosting_commands.delete_hosting(domain=domain, path=path)
        else:
            raise Abort('Deleting aborted.')
    else:
        hosting_commands.delete_path(domain=domain, path=path)


@hosting.command()
@click.pass_context
@click.argument('path')
@click.argument('file')
def update(ctx, path, file):
    domain = validate_domain()
    ctx.obj['hosting_commands'].update_single_file(domain=domain, path=path, file=file)

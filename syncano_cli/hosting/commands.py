# -*- coding: utf-8 -*-
import sys

import click
from syncano_cli.base.options import BottomSpacedOpt, ErrorOpt, TopSpacedOpt
from syncano_cli.hosting.command import HostingCommands
from syncano_cli.hosting.exceptions import DirectoryNotFound
from syncano_cli.hosting.validators import validate_domain, validate_publish


@click.group()
def top_hosting():
    pass


@top_hosting.group()
@click.pass_context
@click.option('--config', help=u'Account configuration file.')
@click.option('--instance-name', help=u'Instance name.')
@click.option('--domain')
def hosting(ctx, config, instance_name, domain):
    """Handle Hosting Socket and Hosting Socket files. Allow to publish static pages to the Syncano Hosting."""
    hosting_commands = HostingCommands(config, instance_name)
    ctx.obj['config'] = config
    ctx.obj['hosting_commands'] = hosting_commands
    ctx.obj['domain'] = hosting_commands.get_config_value(domain, 'domain')
    ctx.obj['instance_name'] = instance_name


@hosting.command()
@click.pass_context
@click.argument('directory', required=False)
def publish(ctx, directory):
    """Allow to publish local files to the Syncano Hosting."""
    # overwrite command with new command that will check local config;
    hosting_commands = HostingCommands(ctx.obj['config'], force_local_check=True)
    directory = hosting_commands.get_config_value(directory, 'directory')
    if not directory:
        raise DirectoryNotFound()
    validate_publish(directory)
    domain = hosting_commands.get_config_value(ctx.obj['domain'], 'domain')
    domain = validate_domain(domain)  # prepared for user defined domains;
    hosting_commands.publish(domain=domain, base_dir=directory)
    url = hosting_commands.get_hosting_url(domain)
    hosting_commands.formatter.write("Your site is published.", TopSpacedOpt())
    hosting_commands.formatter.write("Go to: {url}".format(url=url), BottomSpacedOpt())
    if domain != 'default':
        hosting_commands.formatter.write(
            'You can use: `syncano hosting default {}` to set as default and '
            'make available from `https://{}.syncano.site`'.format(
                domain,
                hosting_commands.instance.name)
        )


@hosting.group(invoke_without_command=True)
@click.pass_context
def list(ctx):
    """List all defined Hosting Sockets in Syncano."""
    if ctx.invoked_subcommand is None:
        hosting_commands = ctx.obj['hosting_commands']
        hosting_commands.print_hostings(
            hostings=hosting_commands.list_hostings()
        )


@list.command()
@click.pass_context
def files(ctx):
    """List all files in given Hosting Socket."""
    domain = ctx.obj['domain']
    domain = validate_domain(domain)
    hosting_commands = ctx.obj['hosting_commands']
    hosting_commands.print_hosting_files(
        domain=domain,
        hosting_files=hosting_commands.list_hosting_files(domain)
    )


@hosting.command()
@click.pass_context
@click.argument('path', required=False)
def delete(ctx, path):
    """Delete the Hosting Socket."""
    domain = ctx.obj['domain']
    domain = validate_domain(domain)
    hosting_commands = ctx.obj['hosting_commands']
    if not path:
        if hosting_commands.prompter.confirm('Do you want to remove whole hosting, domain: {}?'.format(domain)):
            hosting_commands.delete_hosting(domain=domain)
        else:
            hosting_commands.formatter.write('Aborted!', ErrorOpt())
            sys.exit(1)
    else:
        hosting_commands.delete_path(domain=domain, path=path)


@hosting.command()
@click.pass_context
@click.argument('path')
@click.argument('file')
def update(ctx, path, file):
    """Update single file in given Hosting Socket."""
    domain = ctx.obj['domain']
    domain = validate_domain(domain)
    ctx.obj['hosting_commands'].update_single_file(domain=domain, path=path, file=file)

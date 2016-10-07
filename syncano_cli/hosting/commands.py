# -*- coding: utf-8 -*-
import click
from click import Abort
from syncano_cli.hosting.command import HostingCommands
from syncano_cli.hosting.validators import validate_domain, validate_publish


@click.group()
def top_hosting():
    pass


@top_hosting.group()
@click.pass_context
@click.option('--config', help=u'Account configuration file.')
@click.option('--instance-name', help=u'Instance name.')
@click.option('--domain', default='default')
def hosting(ctx, config, instance_name, domain):
    """Handle Hosting Socket and Hosting Socket files. Allow to publish static pages to the Syncano Hosting."""
    hosting_commands = HostingCommands(config)
    hosting_commands.has_setup()
    hosting_commands.set_instance(instance_name)
    ctx.obj['hosting_commands'] = hosting_commands
    ctx.obj['domain'] = domain


@hosting.command()
@click.pass_context
@click.argument('directory')
def publish(ctx, directory):
    """Allow to publish local files to the Syncano Hosting."""
    validate_publish(directory)
    domain = ctx.obj['domain']
    domain = validate_domain(domain)  # prepared for user defined domains;
    hosting_commands = ctx.obj['hosting_commands']
    hosting_commands.publish(domain=domain, base_dir=directory)
    if domain == 'default':
        click.echo(
            "INFO: Your site published. Go to: https://{instance_name}.syncano.site.".format(
                instance_name=hosting_commands.instance.name,
            )
        )
    else:
        click.echo(
            "INFO: Your site published. Go to: https://{instance_name}--{domain}.syncano.site.".format(
                instance_name=hosting_commands.instance.name,
                domain=domain
            )
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
        if click.confirm('Do you want to remove whole hosting, domain: {}?'.format(domain)):
            hosting_commands.delete_hosting(domain=domain)
        else:
            raise Abort()
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

# -*- coding: utf-8 -*-
import click
from syncano_cli.base.command import BaseCommand
from syncano_cli.config import ACCOUNT_CONFIG_PATH


@click.group()
def top_init():
    pass


@top_init.command()
@click.pass_context
@click.option('--config', help=u'Account configuration file.', default=ACCOUNT_CONFIG_PATH)
def init(ctx, config):
    """Register new user and create first Instance."""
    # register new account;
    command = BaseCommand(config)
    command.has_setup()
    command.output_formatter.write_space_line(ctx.parent.get_help(), indent=0)

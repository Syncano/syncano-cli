# -*- coding: utf-8 -*-
import click
from syncano_cli.base.command import BaseCommand
from syncano_cli.base.options import DefaultOpt
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
    command.formatter.write(ctx.parent.get_help(), DefaultOpt(indent=2))

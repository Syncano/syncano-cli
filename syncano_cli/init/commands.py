# -*- coding: utf-8 -*-
import click
from syncano_cli.base.command import BaseCommand
from syncano_cli.base.options import DefaultOpt


@click.group()
def top_init():
    pass


@top_init.command()
@click.pass_context
@click.option('--config', help=u'Account configuration file.')
def init(ctx, config):
    """Register new user and create first Instance."""
    # register new account;
    command = BaseCommand(config)
    command.formatter.write(ctx.parent.get_help(), DefaultOpt(indent=2))

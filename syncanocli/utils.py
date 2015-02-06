import logging

import click

import syncanocli


def print_version(ctx, param, value):
    if not value or ctx.resilient_parsing:
        return
    click.echo(syncanocli.__version__)
    ctx.exit()


def set_loglevel(ctx, param, value):
    loglevel = getattr(logging, value.upper(), None)

    if not isinstance(loglevel, int):
        raise ValueError('Invalid log level: {0}.'.format(loglevel))

    syncanocli.logger.setLevel(loglevel)

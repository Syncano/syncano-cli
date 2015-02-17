import os
import sys
import logging

import click

from syncanocli import __version__
from syncanocli import logger
from . import settings


def print_version(ctx, param, value):
    if not value or ctx.resilient_parsing:
        return
    click.echo(__version__)
    ctx.exit()


def set_loglevel(ctx, param, value):
    value = value.upper()
    loglevel = getattr(logging, value, None)

    if not isinstance(loglevel, int):
        raise click.BadParameter('Invalid log level: {0}.'.format(loglevel))

    logger.setLevel(loglevel)
    return value


class AutodiscoverMultiCommand(click.MultiCommand):

    def list_commands(self, ctx):
        rv = []
        for filename in os.listdir(settings.COMMANDS_FOLDER):
            if filename.endswith('.py') and not filename.startswith('_'):
                rv.append(filename[:-3])
        rv.sort()
        return rv

    def get_command(self, ctx, name):
        try:
            if sys.version_info[0] == 2:
                name = name.encode('ascii', 'replace')
            module_name = 'syncanocli.commands.{0}'.format(name)
            module = __import__(module_name, None, None, ['cli'])
        except ImportError:
            return

        logger.debug('Command loaded: {0}'.format(name))
        return module.cli

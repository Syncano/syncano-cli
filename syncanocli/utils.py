import os
import sys
import logging
from functools import wraps

import click
from click import types

from syncanocli import __version__
from syncanocli import logger
from . import settings


OPTIONS_MAPPING = {
    'StringField': types.StringParamType,
    'IntegerField': types.IntParamType,
    'FloatField': types.FloatParamType,
    'BooleanField': types.BoolParamType,
    'SlugField': types.StringParamType,
    'EmailField': types.StringParamType,
    'ChoiceField': types.Choice,
    'DateField': types.StringParamType,
    'DateTimeField': types.StringParamType,
    'Field': types.StringParamType,
    'HyperlinkedField': types.StringParamType,
    'ModelField': types.StringParamType,
}


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


def field_to_option(name, field, **attrs):
    Type = OPTIONS_MAPPING[field.__class__.__name__]
    type_kwargs = {}

    attrs.setdefault('prompt', True)
    attrs.setdefault('required', field.required)
    attrs.setdefault('type', Type(**type_kwargs))
    return click.option(name, **attrs)


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

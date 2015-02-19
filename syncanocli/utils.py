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


def login_required(f):
    '''Will check if current user is authenticated.
    Should be used after @click.pass_obj or @click.pass_context
    decorator e.g:

        @click.pass_obj
        @login_required
        def dummy(ctx):
            pass
    '''

    @wraps(f)
    def wrapper(ctx, *args, **kwargs):
        context = ctx
        if hasattr(context, 'obj'):
            context = context.obj

        if not context.is_authenticated():
            context.echo.error('You are not authenticated.')
            context.echo('Try to login via "syncano auth login" command.')
            return
        return f(ctx, *args, **kwargs)
    return wrapper


def field_to_option(field):
    name = '--{0}'.format(field.name)
    Type = OPTIONS_MAPPING[field.__class__.__name__]
    type_kwargs = {}

    options = {
        'prompt': True,
        'required': field.required,
        'type': Type(**type_kwargs)
    }
    return click.option(name, **options)


def model_options(model, fields_func=None):
    if not fields_func:
        def fields_func(model):
            fields = reversed(model._meta.fields)
            return [f for f in fields if not f.read_only]

    def decorator(f):

        @wraps(f)
        def inner(*args, **kwargs):
            return f(*args, **kwargs)

        for field in fields_func(model):
            inner = field_to_option(field)(inner)

        return inner
    return decorator


def model_endpoint_fields(model):

    def field_func(model):
        fields = reversed(model._meta.fields)
        return [f for f in fields if f.name in model._meta.endpoint_fields]

    def decorator(f):
        return model_options(model, field_func)(f)

    return decorator


def model_fields_option(*args, **attrs):

    def decorator(f):
        def callback(ctx, param, value):
            fields = [f.strip() for f in value.split(',')]
            return fields

        attrs.setdefault('callback', callback)
        attrs.setdefault('type', str)
        attrs.setdefault('default', '')
        return click.option(*(args or ('--fields', )), **attrs)(f)
    return decorator


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

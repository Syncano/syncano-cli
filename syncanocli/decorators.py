from __future__ import unicode_literals
from functools import wraps

import click

from .utils import field_to_option


class ModelOptions(object):

    def __init__(self, model):
        self.model = model
        self.fields = reversed(self.model._meta.fields)

    def __call__(self, f):

        @wraps(f)
        def inner(*args, **kwargs):
            return f(*args, **kwargs)

        for field in self.get_fields():
            name = self.get_option_name(field)
            fomated_name = self.format_option_name(name)
            attrs = self.get_option_attrs(field)
            inner = field_to_option(fomated_name, field, **attrs)(inner)

        return inner

    def get_fields(self):
        return [f for f in self.fields if not f.read_only]

    def get_option_name(self, field):
        return field.name

    def format_option_name(self, name):
        name = name.replace('_', '-')
        return '--{0}'.format(name)

    def get_option_attrs(self, field):
        return {}


class ModelEndpointOptions(ModelOptions):

    def get_fields(self):
        fields = super(ModelEndpointOptions, self).get_fields()
        return [f for f in fields if f.name in self.model._meta.endpoint_fields]


class ModelUpdateOptions(ModelOptions):
    def __init__(self, model, prefix='set-'):
        super(ModelUpdateOptions, self).__init__(model)
        self.prefix = prefix

    def get_option_name(self, field):
        name = super(ModelUpdateOptions, self).get_option_name(field)
        name = '{0}{1}'.format(self.prefix, name)
        return name


# Aliases
model_options = ModelOptions
model_endpoint_options = ModelEndpointOptions
model_update_options = ModelUpdateOptions


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


def model_fields_option(model, *args, **attrs):

    def decorator(f):
        def callback(ctx, param, value):
            fields = [f.strip() for f in value.split(',')]
            for f in fields:
                if f not in model._meta.field_names:
                    raise click.BadParameter('Invalid choice: {0}.'.format(f))
            return [f for f in model._meta.fields if f.name in fields]

        attrs.setdefault('callback', callback)
        attrs.setdefault('type', str)
        attrs.setdefault('show_default', True)
        attrs.setdefault('default', ','.join(model._meta.field_names))
        return click.option(*(args or ('--fields', )), **attrs)(f)
    return decorator

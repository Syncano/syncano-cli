from __future__ import unicode_literals
from copy import deepcopy
from functools import wraps

import click

from .exceptions import NotAuthenticatedError
from .utils import OPTIONS_MAPPING


class ModelBase(object):
    default_param_decls = ()
    default_attrs = {}

    def __init__(self, model, *param_decls, **attrs):
        self.model = model
        self.fields = self.model._meta.fields
        self.param_decls = param_decls or self.default_param_decls
        self.attrs = deepcopy(self.default_attrs)
        self.attrs.update(attrs)

    def __call__(self, f):

        @wraps(f)
        def inner(*args, **kwargs):
            return f(*args, **kwargs)

        return self.wrap(inner)

    def wrap(self, inner):
        return inner

    def get_fields(self):
        return self.fields

    def get_filed_type(self, field, **attrs):
        cls_name = field.__class__.__name__
        TypeClass = OPTIONS_MAPPING[cls_name]
        return TypeClass(**attrs)

    def get_field_name(self, field):
        return field.name

    def get_field_attrs(self, field):
        self.attrs['type'] = self.get_filed_type(field)
        return self.attrs


class ModelOptions(ModelBase):
    default_attrs = {
        'prompt': True,
        'show_default': True,
    }

    def get_fields(self):
        fields = reversed(super(ModelOptions, self).get_fields())
        return [f for f in fields if not f.read_only]

    def get_field_name(self, field):
        name = field.name.replace('_', '-')
        return '--{0}'.format(name)

    def get_field_attrs(self, field):
        attrs = super(ModelOptions, self).get_field_attrs(field)
        attrs.setdefault('required', field.required)
        return attrs

    def wrap(self, inner):
        for field in self.get_fields():
            name = self.get_field_name(field)
            attrs = self.get_field_attrs(field)
            inner = click.option(name, **attrs)(inner)
        return inner


class ModelArguments(ModelBase):

    def get_fields(self):
        fields = reversed(super(ModelArguments, self).get_fields())
        return [f for f in fields if f.name in self.model._meta.endpoint_fields]

    def wrap(self, inner):
        for field in self.get_fields():
            name = self.get_field_name(field)
            attrs = self.get_field_attrs(field)
            inner = click.argument(name, **attrs)(inner)
        return inner


class ModelFieldsOption(ModelBase):
    default_param_decls = ('--fields', )
    default_attrs = {
        'prompt': False,
        'show_default': True,
    }

    def __init__(self, model, *param_decls, **attrs):
        super(ModelFieldsOption, self).__init__(model)
        self.allowed_fields = self.model._meta.field_names

    def wrap(self, inner):

        def callback(ctx, param, value):
            fields = [f.strip() for f in value.split(',')]
            for f in fields:
                if f not in self.allowed_fields:
                    raise click.BadParameter('Invalid choice: {0}.'.format(f))
            return [f for f in self.fields if f.name in fields]

        self.attrs.setdefault('callback', callback)
        self.attrs.setdefault('type', str)
        self.attrs.setdefault('show_default', True)
        self.attrs.setdefault('default', ','.join(self.allowed_fields))
        return click.option(*self.param_decls, **self.attrs)(inner)


# Aliases
model_options = ModelOptions
model_arguments = ModelArguments
model_fields_option = ModelFieldsOption


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
            raise NotAuthenticatedError()
        return f(ctx, *args, **kwargs)
    return wrapper


def model(model):
    def inner(f):
        @wraps(f)
        def wrapper(ctx, *args, **kwargs):
            context = ctx
            if hasattr(context, 'obj'):
                context = context.obj
            context.model = model
            return f(ctx, *args, **kwargs)
        return wrapper
    return inner

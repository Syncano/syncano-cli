# coding=UTF8
from __future__ import print_function, unicode_literals

import re

from syncano.models.classes import Class

from . import LOG, mute_log

ALLOWED_TYPES = {"array", "boolean", "datetime", "file", "float", "geopoint",
                 "integer", "object", "reference", "relation", "string",
                 "text"}

ALLOWED_PERMISIONS = ('none', 'read', 'create_objects')

# FIXME: We don't require it on backend so, we should not require it in library
Class._meta.get_field('schema').required = False


def field_schema_to_str(schema):
    out = schema['type']
    if schema['type'] == 'reference' and schema['target']:
        out += ' ' + schema['target']
    if schema.get('filter_index', False):
        out += " filtered"
    if schema.get('order_index', False):
        out += " ordered"
    return out


def expect(tokens, regexp, message=''):
    try:
        value = tokens.pop(0).lower()
    except IndexError:
        value = ''
    if not re.match(regexp, value):
        if message:
            message = ' ' + message
        raise ValueError('Unexpected token {0}.{1}'.format(value, message))
    return value


def schema_str_to_field(schema_str):
    """
    >>> schema_str_to_field('integer') == {u'type': u'integer'}
    True

    >>> schema_str_to_field('reference www') == {u'type': u'reference',\
            u'target': u'www'}
    True

    >>> schema_str_to_field('reference www filtered') == \
            {u'filter_index': True, u'type': u'reference', u'target': u'www'}
    True

    >>> schema_str_to_field('reference www filtered filtered')
    Traceback (most recent call last):
    ...
    ValueError: Unexpected token filtered. Expected ordered or $ keywords.

    >>> schema_str_to_field('integer filtered ordered') \
            == schema_str_to_field('integer ordered filtered')
    True

    >>> schema_str_to_field('integer aaa') #doctest: +ELLIPSIS
    Traceback (most recent call last):
    ...
    ValueError: Unexpected token aaa. Expected filtered or ordered or $ ...
    """
    bits = schema_str.split()
    schema = {}
    typ = expect(bits, '|'.join(ALLOWED_TYPES),
                 'Expected one of {0}.'.format(', '.join(ALLOWED_TYPES)))
    schema['type'] = typ
    if typ == 'reference' and bits:
        schema['target'] = expect(bits, '\w+', 'Expected reference target.')
    rest = ['filtered', 'ordered', '$']
    while bits:
        t = expect(bits, '|'.join(rest),
                   'Expected {0} keywords.'.format(' or '.join(rest)))
        if t == 'filtered':
            schema['filter_index'] = True
        elif t == 'ordered':
            schema['order_index'] = True
        else:
            break
        rest.remove(t)
    return schema


def pull_classes(instance, include, update_dict=None):
    out = {}
    if update_dict is not None:
        out = update_dict
    for cls in instance.classes.all():
        if include and cls.name not in include:
            continue
        out[cls.name] = dict(
            group_permissions=cls.group_permissions,
            other_permissions=cls.other_permissions,
            fields={f['name']: str(field_schema_to_str(f)) for f in cls.schema}
        )
    return out


def push_classes(instance, class_dict):
    LOG.debug('Pushing classes.')
    for name, config in class_dict.iteritems():
        LOG.debug('Pushing class {0}'.format(name))
        try:
            klass = instance.classes.get(name=name)
            LOG.debug('Found class {0}'.format(name))
        except instance.classes.model.DoesNotExist:
            klass = instance.clasess.model(name=name)
            LOG.debug('Class {0} not found. Creating new one'.format(name))
        schema = []
        for name, field_config in config['fields'].iteritems():
            field = {'name': name}
            field.update(schema_str_to_field(field_config))
            schema.append(field)
        klass.schema = schema

        with mute_log():
            klass.save()
        LOG.debug('Class {0} pushed.'.format(name))


def validate_class(class_dict):
    fields = class_dict.get('fields')

    if fields is None:
        raise ValueError('You should have some fields defined.')

    if not isinstance(fields, dict):
        raise ValueError('Fields should be a dictionary.')

    for name, spec in fields.iteritems():
        try:
            schema_str_to_field(spec)
        except ValueError as e:
            raise ValueError('{0}: {1.message}'.format(name, e))

    for perm in ('group_permissions', 'other_permissions'):
        val = class_dict.get(perm, None)
        if val is not None and val not in ALLOWED_PERMISIONS:
            raise ValueError('{0} should be one of: {1}.'.format(
                perm, ', '.join(ALLOWED_PERMISIONS)))


def validate_classes(classes_dict):
    for name, spec in classes_dict.iteritems():
        validate_class(spec)

        for field, field_spec in spec['fields'].items():
            field_spec = schema_str_to_field(field_spec)

            if field_spec['type'] != 'reference':
                continue

            target = field_spec['target']

            if target != 'self' and target not in classes_dict:
                raise ValueError(
                    '{0}.{1} references not defined class {2}'
                    .format(name, field, field_spec['target'])
                )

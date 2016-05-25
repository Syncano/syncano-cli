# -*- coding: utf-8 -*-
import argparse
import os
from collections import defaultdict

import six


def argument(*args, **kwargs):
    def wrapper(f):
        if not hasattr(f, 'arguments'):
            f.arguments = []
        f.arguments.append((args, kwargs))
        return f
    return wrapper


class EnvDefault(argparse.Action):
    #  http://stackoverflow.com/questions/10551117/setting-options-from-environment-variables-when-using-argparse
    def __init__(self, envvar, required=True, default=None, nargs=None, **kwargs):
        if not default and envvar:
            if envvar in os.environ:
                default = os.environ[envvar]
        if required and default:
            required = False
            nargs = '?'
        super(EnvDefault, self).__init__(default=default, required=required, nargs=nargs, **kwargs)

    def __call__(self, parser, namespace, values, option_string=None):
        setattr(namespace, self.dest, values)


class CommandContainer(type):
    commands = defaultdict(dict)

    def __new__(cls, name, bases, attrs):
        klass = super(CommandContainer, cls).__new__(cls, name, bases, attrs)
        cls._register(klass, name, klass.run)
        return klass

    @classmethod
    def _register(cls, klass, name, command):
        cls.commands[klass.namespace][name.lower()] = command


def add_commands(subparsers, container):
    for command_name, command in six.iteritems(container):
        high_lvl_subparser = subparsers.add_parser(command_name, description=command.__doc__)
        for args, kwargs in getattr(command, 'arguments', []):
            high_lvl_subparser.add_argument(*args, **kwargs)
        high_lvl_subparser.set_defaults(func=command)


def parse_arguments(args):
    ACCOUNT_CONFIG_PATH = os.path.join(os.path.expanduser('~'), '.syncano')

    parser = argparse.ArgumentParser(
        description='Syncano command line tools.'
    )
    parser.add_argument('--file', '-f', default='syncano.yml',
                        help='Instance configuraion file.')
    parser.add_argument('--config', default=ACCOUNT_CONFIG_PATH,
                        help='Account configuration file.')
    parser.add_argument('--key', default=os.environ.get('SYNCANO_API_KEY', None),
                        help='override ACCOUNT_KEY used for authentication.')

    subparsers = parser.add_subparsers(
        title='commands',
        description='valid commands'
    )

    # add toplevel commands;
    add_commands(subparsers=subparsers, container=CommandContainer.commands['toplevel'])

    for sub_name, functions in six.iteritems(CommandContainer.commands):
        if sub_name == 'toplevel':
            continue

        first_lvl_commands = subparsers.add_parser(sub_name)
        first_lvl_commands_subparsers = first_lvl_commands.add_subparsers(
            title='subcommand',
            description='valid subcommands'
        )
        add_commands(subparsers=first_lvl_commands_subparsers, container=functions)

    return parser.parse_args(args)

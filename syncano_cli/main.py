# -*- coding: utf-8 -*-
from __future__ import print_function, unicode_literals

import argparse
import os
import sys
from ConfigParser import ConfigParser, NoOptionError

import six
from syncano_cli import LOG
from syncano_cli.commands import Configure, Login, Parse, Pull, Push  # noqa
from syncano_cli.commands_base import CommandContainer
from syncano_cli.sync.project import Project

ACCOUNT_KEY = ''

ACCOUNT_CONFIG = ConfigParser()


def add_commands(subparsers, container):
    for command_name, command in six.iteritems(container):
        high_lvl_subparser = subparsers.add_parser(command_name, description=command.__doc__)
        for args, kwargs in getattr(command, 'arguments', []):
            high_lvl_subparser.add_argument(*args, **kwargs)
        high_lvl_subparser.set_defaults(func=command)


def cli(args):
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

    namespace = parser.parse_args(args)
    namespace.project = Project.from_config(namespace.file)

    read = ACCOUNT_CONFIG.read(namespace.config)
    if read and not namespace.key:
        try:
            namespace.key = ACCOUNT_CONFIG.get('DEFAULT', 'key')
        except NoOptionError:
            LOG.error('Do a login first.')

    try:
        namespace.func(namespace)
    except ValueError as e:
        LOG.error(e.message)


def main():
    cli(sys.argv[1:])


if __name__ == "__main__":
    main()

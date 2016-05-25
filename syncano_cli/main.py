# -*- coding: utf-8 -*-
from __future__ import print_function, unicode_literals

import sys
from ConfigParser import ConfigParser, NoOptionError

from syncano_cli import LOG
from syncano_cli.commands import Configure, Login, Parse, Pull, Push  # noqa
from syncano_cli.commands_base import parse_arguments
from syncano_cli.sync.project import Project

ACCOUNT_KEY = ''

ACCOUNT_CONFIG = ConfigParser()


def cli(args):
    namespace = parse_arguments(args)
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

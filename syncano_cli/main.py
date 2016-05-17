# coding=UTF8
from __future__ import print_function, unicode_literals

import argparse
import logging
import os
import sys
from ConfigParser import ConfigParser
from getpass import getpass

import syncano
from syncano.exceptions import SyncanoException

from .project import Project

ACCOUNT_KEY = ''

ACCOUNT_CONFIG = ConfigParser()

COMMANDS = {}

LOG = logging.getLogger()
CONSOLE_HANDLER = logging.StreamHandler(sys.stderr)


def command(func):
    COMMANDS[func.func_name] = func
    return func


def argument(*args, **kwargs):
    def wrapper(f):
        if not hasattr(f, 'arguments'):
            f.arguments = []
        f.arguments.append((args, kwargs))
        return f
    return wrapper


def setup_logging():
    root = logging.getLogger()
    root.addHandler(CONSOLE_HANDLER)
    root.setLevel(logging.DEBUG)
    # disable requests logging
    logging.getLogger("requests").propagate = False


@command
def login(args):
    """
    Log in to syncano using email and password and store ACCOUNT_KEY
    in configuration file.
    """
    email = os.environ.get('SYNCANO_EMAIL', None)
    if email is None:
        email = raw_input("email: ")
    password = os.environ.get('SYNCANO_PASSWORD', None)
    if password is None:
        password = getpass("password: ").strip()
    connection = syncano.connect().connection()
    try:
        ACCOUNT_KEY = connection.authenticate(email=email, password=password)
        ACCOUNT_CONFIG.set('DEFAULT', 'key', ACCOUNT_KEY)
        with open(args.config, 'wb') as fp:
            ACCOUNT_CONFIG.write(fp)
    except SyncanoException as error:
        print(error)


@command
@argument('-s', '--script', action='append', dest='scripts',
          help="Pull only this script from syncano")
@argument('-c', '--class', action='append', dest='classes',
          help="Pull only this class from syncano")
@argument('-a', '--all', action='store_true',
          help="Force push all configuration")
@argument('instance', help="Destination instance name")
def push(context):
    """
    Push configuration changes to syncano.
    """
    con = syncano.connect(api_key=context.key)
    instance = con.instances.get(name=context.instance)
    context.project.push_to_instance(instance, classes=context.classes,
                                     scripts=context.scripts, all=context.all)


@argument('instance', help="Source instance name")
@argument('script', help="script label or script name")
def run(args):
    """Execute script on syncano."""
    pass


@command
@argument('-s', '--script', action='append', dest='scripts',
          help="Pull only this script from syncano")
@argument('-c', '--class', action='append', dest='classes',
          help="Pull only this class from syncano")
@argument('-a', '--all', action='store_true',
          help="Pull all classes/scripts from syncano")
@argument('instance', help="Source instance name")
def pull(context):
    """
    Pull configuration from syncano and store it in current directory.
    Updates syncano.yml configuration file, and places scripts in scripts
    directory.
    When syncano.yml file exists. It will pull only objects defined in
    configuration file. If you want to pull all objects from syncano use
    -a/--all flag.
    """
    con = syncano.connect(api_key=context.key)
    instance = con.instances.get(name=context.instance)
    context.project.update_from_instance(instance, context.all,
                                         context.classes, context.scripts)
    context.project.write(context.file)


def main():
    setup_logging()
    ACCOUNT_CONFIG_PATH = os.path.join(os.path.expanduser('~'), '.syncano')

    parser = argparse.ArgumentParser(
        description='Syncano command line tools.'
    )
    parser.add_argument('--file', '-f', default='syncano.yml',
                        help='Instance configuraion file.')
    parser.add_argument('--config', default=ACCOUNT_CONFIG_PATH,
                        help='Account configuration file.')
    parser.add_argument('--key', default=os.environ.get('SYNCANO_API_KEY', ''),
                        help='override ACCOUNT_KEY used for authentication.')

    subparsers = parser.add_subparsers(
        title='subcommands',
        description='valid subcommands'
    )

    for fname, func in COMMANDS.iteritems():
        subparser = subparsers.add_parser(fname, description=func.__doc__)
        for args, kwargs in getattr(func, 'arguments', []):
            subparser.add_argument(*args, **kwargs)
        subparser.set_defaults(func=func)
    namespace = parser.parse_args()

    namespace.project = Project.from_config(namespace.file)

    read = ACCOUNT_CONFIG.read(namespace.config)
    if read and not namespace.key:
        namespace.key = ACCOUNT_CONFIG.get('DEFAULT', 'key')

    try:
        namespace.func(namespace)
    except ValueError as e:
        LOG.error(e.message)

if __name__ == "__main__":
    main()

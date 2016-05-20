# coding=UTF8
from __future__ import print_function, unicode_literals

import argparse
import os
from collections import defaultdict
from ConfigParser import ConfigParser, NoOptionError
from getpass import getpass

import six
import syncano
from syncano.exceptions import SyncanoException
from syncano_cli import LOG
from syncano_cli.parse_to_syncano.config import config
from syncano_cli.parse_to_syncano.migrations.transfer import SyncanoTransfer
from syncano_cli.parse_to_syncano.moses import check_configuration, force_configuration_overwrite, print_configuration
from syncano_cli.sync.project import Project

ACCOUNT_KEY = ''

ACCOUNT_CONFIG = ConfigParser()

COMMANDS = defaultdict(dict)
HIGH_LVL_COMMANDS = {}


class Command(object):

    def __init__(self, namespace):
        self.namespace = namespace

    def __call__(self, func):
        COMMANDS[self.namespace][func.func_name] = func
        return func


class HighLvlCommand(object):

    def __call__(self, func):
        HIGH_LVL_COMMANDS[func.func_name] = func
        return func


class Argument(object):
    def __init__(self, *args, **kwargs):
        self.args = args
        self.kwargs = kwargs

    def __call__(self, func):
        def wrapper(f):
            if not hasattr(f, 'arguments'):
                f.arguments = []
            f.arguments.append((self.args, self.kwargs))
            return f
        return wrapper(func)


@HighLvlCommand()
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


@Command('sync')
@Argument('-s', '--script', action='append', dest='scripts',
          help="Pull only this script from syncano")
@Argument('-c', '--class', action='append', dest='classes',
          help="Pull only this class from syncano")
@Argument('-a', '--all', action='store_true',
          help="Force push all configuration")
@Argument('instance', help="Destination instance name")
def push(context):
    """
    Push configuration changes to syncano.
    """
    con = syncano.connect(api_key=context.key)
    instance = con.instances.get(name=context.instance)
    context.project.push_to_instance(instance, classes=context.classes,
                                     scripts=context.scripts, all=context.all)


@Argument('instance', help="Source instance name")
@Argument('script', help="script label or script name")
def run(args):
    """Execute script on syncano."""
    pass


@Command('sync')
@Argument('-s', '--script', action='append', dest='scripts',
          help="Pull only this script from syncano")
@Argument('-c', '--class', action='append', dest='classes',
          help="Pull only this class from syncano")
@Argument('-a', '--all', action='store_true',
          help="Pull all classes/scripts from syncano")
@Argument('instance', help="Source instance name")
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


@Command('import')
def parse(context):
    """
    Synchronize the parse data object with syncano data objects;
    """
    check_configuration(silent=True)
    application_id = config.get('P2S', 'PARSE_APPLICATION_ID')
    instance_name = config.get('P2S', 'SYNCANO_INSTANCE_NAME')
    confirmation = raw_input('Are you sure you want to copy your data from PARSE application ({application_id})'
                             ' to the syncano isntance ({instance_name})? Y/N [Y]: '.format(
                                 application_id=application_id,
                                 instance_name=instance_name)
                             ) or 'Y'

    if confirmation not in ['Y', 'YES', 'y', 'yes']:
        LOG.info('Transfer aborted.')
        return

    transfer = SyncanoTransfer()
    transfer.through_the_red_sea()


@Command('import')
@Argument('-c', '--current', action='store_true', help="Show current configuration.")
@Argument('-f', '--force', action='store_true', help="Froce to overwrite previous config.")
def configure(context):
    """
    Configure the data needed for connection to the parse and syncano;
    """
    if context.current:
        print_configuration()
    elif context.force:
        force_configuration_overwrite()
    else:
        check_configuration()


def main():
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
        title='commands',
        description='valid commands'
    )

    for command_name, command in six.iteritems(HIGH_LVL_COMMANDS):
        high_lvl_subparser = subparsers.add_parser(command_name, description=command.__doc__)
        for args, kwargs in getattr(command, 'arguments', []):
            high_lvl_subparser.add_argument(*args, **kwargs)
        high_lvl_subparser.set_defaults(func=command)

    for sub_name, functions in six.iteritems(COMMANDS):
        first_lvl_commands = subparsers.add_parser(sub_name)
        first_lvl_commands_subparser = first_lvl_commands.add_subparsers(
            title='subcommand',
            description='valid subcommands'
        )
        for fname, func in six.iteritems(functions):
            subparser = first_lvl_commands_subparser.add_parser(fname, description=func.__doc__)
            for args, kwargs in getattr(func, 'arguments', []):
                subparser.add_argument(*args, **kwargs)
            subparser.set_defaults(func=func)

    namespace = parser.parse_args()

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

if __name__ == "__main__":
    main()

import os

import click

import syncanocli


CONTEXT = {
    'auto_envvar_prefix': 'SYNCANO',
}

LOGLEVELS = [
    'ERROR',
    'WARNING',
    'INFO',
    'DEBUG',
    'NOTSET',
]

COMMANDS_FOLDER = os.path.abspath(
    os.path.join(os.path.dirname(__file__), 'commands')
)

CONFIG_FILENAME = '.syncano'
CONFIG_DIR_SETTINGS = {
    'app_name': syncanocli.__title__,
    'roaming': True,
    'force_posix': False
}
CONFIG_DEFAULT_PATH = os.path.join(
    click.get_app_dir(**CONFIG_DIR_SETTINGS),
    CONFIG_FILENAME
)

ALIASES = {
    'login': 'auth.login',
    'logout': 'auth.logout',
}

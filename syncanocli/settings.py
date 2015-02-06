import os

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
CONFIG = {
    'app_name': syncanocli.__title__,
    'roaming': True,
    'force_posix': False
}

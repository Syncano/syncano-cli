# -*- coding: utf-8 -*-

from syncano_cli.base.exceptions import CLIBaseException


class MissingRequestDataException(CLIBaseException):
    default_message = u'--data option should be provided when method {} is used'

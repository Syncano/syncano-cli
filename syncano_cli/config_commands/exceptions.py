# -*- coding: utf-8 -*-

from syncano_cli.base.exceptions import CLIBaseException


class VariableInConfigException(CLIBaseException):
    default_message = u'`{}` already in config, use `syncano config modify` instead.'


class VariableNotFoundException(CLIBaseException):
    default_message = u'Variable `{}` not found.'

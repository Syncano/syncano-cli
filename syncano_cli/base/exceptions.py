# -*- coding: utf-8 -*-

from click import ClickException


class CLIBaseException(ClickException):

    default_message = u'A CLI processing exception.'

    def __init__(self, message=None, format_args=None):
        message = message or self.default_message
        if format_args:
            message = message.format(*format_args)
        super(CLIBaseException, self).__init__(message)


class SyncanoLibraryException(CLIBaseException):
    pass


class JSONParseException(CLIBaseException):
    default_message = u'Invalid JSON data. Parse error.'


class BadCredentialsException(CLIBaseException):
    default_message = u'Wrong login credentials provided.'


class NotLoggedInException(CLIBaseException):
    default_message = u'Please log in to your account: `syncano login`.'


class InstanceNotFoundException(CLIBaseException):
    default_message = u'Instance `{}` not found.'


class DataParseException(CLIBaseException):
    default_message = u'Wrong data format: use -d key=value'

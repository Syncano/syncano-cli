# -*- coding: utf-8 -*-

from syncano_cli.base.exceptions import CLIBaseException


class PathNotFoundException(CLIBaseException):
    default_message = u'File `{}` not found.'


class NoHostingFoundException(CLIBaseException):
    default_message = u'Hosting with domain `{}` - not found. Exit.'


class NotADirectoryException(CLIBaseException):
    default_message = u'You should provide a project root directory here.'

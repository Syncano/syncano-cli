# -*- coding: utf-8 -*-

from syncano_cli.base.exceptions import CLIBaseException


class PathNotFoundException(CLIBaseException):
    default_message = u'File `{}` not found.'


class UnicodeInPathException(CLIBaseException):
    default_message = u'Unicode characters in path are not supported. Check the files names.'


class NoDefaultHostingFoundException(CLIBaseException):
    default_message = u'No default hosting found. Exit.'


class NotADirectoryException(CLIBaseException):
    default_message = u'You should provide a project root directory here.'

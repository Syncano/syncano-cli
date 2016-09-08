# -*- coding: utf-8 -*-

from syncano_cli.base.exceptions import CLIBaseException


class InstancesNotFoundException(CLIBaseException):
    default_message = u'No instances found.'


class InstanceNameMismatchException(CLIBaseException):
    default_message = u'Provided instance name do not match.'

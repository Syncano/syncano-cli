# -*- coding: utf-8 -*-

import os

from syncano_cli.hosting.exceptions import NotADirectoryException


def validate_publish(directory):
    if not os.path.isdir(directory):
        raise NotADirectoryException()


def validate_domain(provided_domain=None):
    return 'default' if not provided_domain else provided_domain

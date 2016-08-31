# -*- coding: utf-8 -*-

import os
import sys

import click


def validate_publish(directory):
    if not os.path.isdir(directory):
        click.echo(u'ERROR: You should provide a project root directory here.')
        sys.exit(1)


def validate_domain(provided_domain=None):
    return 'default' if not provided_domain else provided_domain

# -*- coding: utf-8 -*-
import argparse
import os
from collections import defaultdict


def argument(*args, **kwargs):
    def wrapper(f):
        if not hasattr(f, 'arguments'):
            f.arguments = []
        f.arguments.append((args, kwargs))
        return f
    return wrapper


class EnvDefault(argparse.Action):
    #  http://stackoverflow.com/questions/10551117/setting-options-from-environment-variables-when-using-argparse
    def __init__(self, envvar, required=True, default=None, nargs=None, **kwargs):
        if not default and envvar:
            if envvar in os.environ:
                default = os.environ[envvar]
        if required and default:
            required = False
            nargs = '?'
        super(EnvDefault, self).__init__(default=default, required=required, nargs=nargs, **kwargs)

    def __call__(self, parser, namespace, values, option_string=None):
        setattr(namespace, self.dest, values)


class CommandContainer(type):
    commands = defaultdict(dict)

    def __new__(cls, name, bases, attrs):
        klass = super(CommandContainer, cls).__new__(cls, name, bases, attrs)
        cls._register(klass, name, klass.run)
        return klass

    @classmethod
    def _register(cls, klass, name, command):
        cls.commands[klass.namespace][name.lower()] = command

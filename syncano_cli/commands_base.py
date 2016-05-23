# -*- coding: utf-8 -*-
from collections import defaultdict


def argument(*args, **kwargs):
    def wrapper(f):
        if not hasattr(f, 'arguments'):
            f.arguments = []
        f.arguments.append((args, kwargs))
        return f
    return wrapper


class CommandContainer(type):
    commands = defaultdict(dict)

    def __new__(cls, name, bases, attrs):
        klass = super(CommandContainer, cls).__new__(cls, name, bases, attrs)
        cls._register(klass, name, klass.run)
        return klass

    @classmethod
    def _register(cls, klass, name, command):
        cls.commands[klass.namespace][name.lower()] = command

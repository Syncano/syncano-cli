# -*- coding: utf-8 -*-

import sys

import click
import six


class ConfigCommand(object):

    def __init__(self, instance):
        self.instance = instance

    def config_show(self):
        config = self.instance.get_config()
        click.echo('Config for instance {}'.format(self.instance.name))
        for name, value in six.iteritems(config):
            click.echo('{:20}: {}'.format(name, value))

    def add(self, name, value):
        config = self.instance.get_config()
        if name in config:
            click.echo('ERROR: `{}` already in config, use `syncano config modify` instead.'.format(name))
            sys.exit(1)
        config.update({name: value})
        self.instance.set_config(config)
        click.echo('Variable `{}` set to `{}`.'.format(name, value))

    def modify(self, name, value):
        config = self.instance.get_config()
        config.update({name: value})
        self.instance.set_config(config)
        click.echo('Variable `{}` set to `{}`.'.format(name, value))

    def delete(self, name):
        config = self.instance.get_config()
        if name in config:
            config.pop(name)
        else:
            click.echo('ERROR: variable `{}` not found.'.format(name))
            sys.exit(1)
        self.instance.set_config(config)
        click.echo('Variable `{}` removed.'.format(name))

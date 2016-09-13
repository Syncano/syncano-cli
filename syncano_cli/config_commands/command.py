# -*- coding: utf-8 -*-

import click
import six
from syncano_cli.base.command import BaseInstanceCommand
from syncano_cli.config_commands.exceptions import VariableInConfigException, VariableNotFoundException


class ConfigCommand(BaseInstanceCommand):

    def config_show(self):
        config = self.instance.get_config()
        click.echo('Config for instance {}'.format(self.instance.name))
        for name, value in six.iteritems(config):
            click.echo('{:20}: {}'.format(name, value))

    def add(self, name, value):
        config = self.instance.get_config()
        if name in config:
            raise VariableInConfigException(format_args=[name])
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
            raise VariableNotFoundException(format_args=[name])
        self.instance.set_config(config)
        click.echo('Variable `{}` removed.'.format(name))

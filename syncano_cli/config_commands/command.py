# -*- coding: utf-8 -*-

import six
from syncano_cli.base.command import BaseInstanceCommand
from syncano_cli.config_commands.exceptions import VariableInConfigException, VariableNotFoundException


class ConfigCommand(BaseInstanceCommand):

    def config_show(self):
        config = self.instance.get_config()
        self._show_config(config)

    def _show_config(self, config):
        self.output_formatter.write_space_line('Config for Instance {}'.format(self.instance.name), bottom=False)
        for name, value in six.iteritems(config):
            self.output_formatter.write_line('{:20}: {}'.format(name, value), indent=2)
        if not config:
            self.output_formatter.write_line('No config specified yet.', indent=2)
        self.output_formatter.finalize()

    def add(self, name, value):
        config = self.instance.get_config()
        if name in config:
            raise VariableInConfigException(format_args=[name])
        config.update({name: value})
        self.instance.set_config(config)
        self.output_formatter.write_space_line('Variable `{}` set to `{}` in instance `{}`.'.format(
            name, value, self.instance.name), bottom=False)
        self._show_config(config)

    def modify(self, name, value):
        config = self.instance.get_config()
        config.update({name: value})
        self.instance.set_config(config)
        self.output_formatter.write_space_line('Variable `{}` set to `{}` in instance `{}`.'.format(
            name, value, self.instance.name), bottom=False)
        self._show_config(config)

    def delete(self, name):
        config = self.instance.get_config()
        if name in config:
            config.pop(name)
        else:
            raise VariableNotFoundException(format_args=[name])
        self.instance.set_config(config)
        self.output_formatter.write_space_line('Variable `{}` removed from in instance `{}`.'.format(
            name, self.instance.name), bottom=False)
        self._show_config(config)

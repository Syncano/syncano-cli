# -*- coding: utf-8 -*-

from syncano_cli.base.command import BaseInstanceCommand
from syncano_cli.base.options import TopSpacedOpt
from syncano_cli.config_commands.exceptions import VariableInConfigException, VariableNotFoundException


class ConfigCommand(BaseInstanceCommand):

    def config_show(self):
        config = self.instance.get_config()
        self._show_config(config)

    def _show_config(self, config):
        self.output_formatter.write_space('Config for Instance {}'.format(self.instance.name),
                                          space_bottom=False)
        self.output_formatter.display_config(config)
        self.output_formatter.empty_line()

    def add(self, name, value):
        config = self.instance.get_config()
        if name in config:
            raise VariableInConfigException(format_args=[name])
        config.update({name: value})
        self.instance.set_config(config)
        self.output_formatter.write_space('Variable `{}` set to `{}` in instance `{}`.'.format(
            name, value, self.instance.name), TopSpacedOpt())
        self._show_config(config)

    def modify(self, name, value):
        config = self.instance.get_config()
        config.update({name: value})
        self.instance.set_config(config)
        self.output_formatter.write_space('Variable `{}` set to `{}` in instance `{}`.'.format(
            name, value, self.instance.name), TopSpacedOpt())
        self._show_config(config)

    def delete(self, name):
        config = self.instance.get_config()
        if name in config:
            config.pop(name)
        else:
            raise VariableNotFoundException(format_args=[name])
        self.instance.set_config(config)
        self.output_formatter.write_space('Variable `{}` removed from in instance `{}`.'.format(
            name, self.instance.name), TopSpacedOpt())
        self._show_config(config)

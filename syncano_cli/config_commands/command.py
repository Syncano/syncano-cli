# -*- coding: utf-8 -*-
from syncano_cli.base.command import BaseCommand
from syncano_cli.base.options import TopSpacedOpt
from syncano_cli.config_commands.exceptions import VariableInConfigException, VariableNotFoundException


class ConfigCommand(BaseCommand):

    def config_show(self):
        config = self.instance.get_config()
        self._show_config(config)

    def _show_config(self, config):
        self.formatter.write('Config for Instance {}'.format(self.instance.name), TopSpacedOpt())
        self.formatter.display_config(config)

    def add(self, name, value):
        config = self.instance.get_config()
        if name in config:
            raise VariableInConfigException(format_args=[name])
        config.update({name: value})
        self.instance.set_config(config)
        self.formatter.write('Variable `{}` set to `{}` in instance `{}`.'.format(
            name, value, self.instance.name), TopSpacedOpt())
        self._show_config(config)

    def modify(self, name, value):
        config = self.instance.get_config()
        config.update({name: value})
        self.instance.set_config(config)
        self.formatter.write('Variable `{}` set to `{}` in instance `{}`.'.format(
            name, value, self.instance.name), TopSpacedOpt())
        self._show_config(config)

    def delete(self, name):
        config = self.instance.get_config()
        if name in config:
            config.pop(name)
        else:
            raise VariableNotFoundException(format_args=[name])
        self.instance.set_config(config)
        self.formatter.write('Variable `{}` removed from instance `{}`.'.format(
            name, self.instance.name), TopSpacedOpt())
        self._show_config(config)

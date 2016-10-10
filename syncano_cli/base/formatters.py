# -*- coding: utf-8 -*-
import click
import six


class ColorStylesE(object):
    INFO = 'green'
    PROMPT = 'cyan'
    WARNING = 'yellow'
    ERROR = 'red'


class OutputFormatter(object):

    indent = '    '
    not_set = '-- not set --'

    def __init__(self):
        self.color_schema = ColorStylesE()

    def write_line(self, text, color=None, indent=1):
        kwargs = {'fg': color or self.color_schema.INFO}
        if indent:
            text = '{}{}'.format(self.indent * indent, text)
        click.echo(click.style(text, **kwargs))

    def write_space_line(self, text, color=None, top=True, bottom=True, indent=1):
        if top:
            click.echo()
        self.write_line(text, color=color, indent=indent)
        if bottom:
            click.echo()

    @classmethod
    def finalize(cls):
        click.echo()

    def separator(self):
        self.write_line(70 * '-', color=self.color_schema.WARNING)

    def display_config(self, config):
        for name, value in six.iteritems(config):
            self.write_line('{:20}: {}'.format(name, value))
        if not config:
            self.write_line('No config specified yet.', indent=2)

    def format_object(self, dictionary, indent=1):
        indent += 1
        for key, value in six.iteritems(dictionary):
            if isinstance(value, dict):
                self.write_line('{}:'.format(key), indent=indent)
                self.format_object(value, indent=indent)
            elif isinstance(value, list):
                self._format_list(value, key=key, indent=indent)
            else:
                self.write_line('{}: {}'.format(key, value), indent=indent)

    def _format_list(self, data_list, key, indent):
        try:
            value = ', '.join(data_list)
        except TypeError:
            value = data_list
        if not key:
            self.write_line('{}'.format(value), indent=indent)
        else:
            self.write_line('{}: {}'.format(key, value), indent=indent)

# -*- coding: utf-8 -*-
import click


class ColorStylesE(object):
    INFO = 'green'
    PROMPT = 'cyan'
    WARNING = 'yellow'
    ERROR = 'red'


class OutputFormatter(object):

    indent = '    '

    def __init__(self):
        self.color_schema = ColorStylesE()

    def write_line(self, text, color=None, indent=False):
        kwargs = {'fg': color or self.color_schema.INFO}
        if indent:
            text = '{}{}'.format(self.indent, text)
        click.echo(click.style(text, **kwargs))

    def write_space_line(self, text, color=None, top=True, bottom=True, indent=False):
        if top:
            click.echo()
        self.write_line(text, color=color, indent=indent)
        if bottom:
            click.echo()

    @classmethod
    def finalize(cls):
        click.echo()

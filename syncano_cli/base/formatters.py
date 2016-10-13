# -*- coding: utf-8 -*-
import click
import six
from syncano_cli.base.options import BottomSpacedOpt, ColorSchema, DefaultOpt, OptionsBase, WarningOpt


class Formatter(object):

    indent = '    '
    not_set = '-- not set --'

    def write(self, single_line, *options):
        option = self.get_options(options)
        styles = option.map_click()
        single_line = self._indent(single_line, option)
        self._write(single_line, option, **styles)

    def write_lines(self, lines, *options):
        lines = lines.splitlines() if isinstance(lines, six.string_types) else lines
        for line in lines:
            self.write(line, *options)

    def write_block(self, lines, *options):
        self.write_lines(lines, *options)
        self.separator()

    @classmethod
    def empty_line(cls):
        click.echo()

    def separator(self, size=70, indent=1):
        self.write(size * '-', DefaultOpt(indent=indent), WarningOpt(), BottomSpacedOpt())

    def display_config(self, config):
        for name, value in six.iteritems(config):
            self.write('{}{:20} {}'.format(
                self.indent,
                click.style(name, fg=ColorSchema.PROMPT),
                click.style(value, fg=ColorSchema.INFO)
            ))
        if not config:
            self.write('No config specified yet.', DefaultOpt(indent=2))

    def get_options(self, options):
        option_list = list(options) or []
        option_list.insert(0, DefaultOpt())
        return OptionsBase.build_options(option_list)

    def format_object(self, dictionary, indent=1, skip_fields=None):
        skip_fields = skip_fields or []
        indent += 1
        for key, value in six.iteritems(dictionary):
            if isinstance(value, dict):
                self.write('{}:'.format(click.style(key, fg=ColorSchema.PROMPT)), DefaultOpt(indent=indent))
                self.format_object(value, indent=indent, skip_fields=skip_fields)
            elif isinstance(value, list):
                self.format_list(value, key=key, indent=indent)
            else:
                if key in skip_fields:
                    continue
                self.write('{}: {}'.format(
                    click.style(key, fg=ColorSchema.PROMPT),
                    click.style(value, fg=ColorSchema.INFO)
                ), DefaultOpt(indent=indent))

    def format_list(self, data_list, key=None, indent=2, skip_fields=None):
        skip_fields = skip_fields or []
        for el in data_list:
            if isinstance(el, dict):
                self.format_object(el, indent=indent, skip_fields=skip_fields)
            else:
                if key:
                    self.write('{}: {}'.format(
                        click.style(key, fg=ColorSchema.PROMPT),
                        click.style(el, fg=ColorSchema.INFO)
                    ), DefaultOpt(indent=indent))
                else:
                    self.write('{}'.format(el), DefaultOpt(indent=indent))
            self.empty_line()

    def _write(self, line, options, **styles):
        if options.space_top:
            self.empty_line()

        click.echo(click.style(line, **styles))

        if options.space_bottom:
            self.empty_line()

    def _indent(self, line, options):
        return '{}{}'.format(self.indent * options.indent, line)

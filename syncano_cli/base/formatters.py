# -*- coding: utf-8 -*-
import click
import six
from syncano_cli.base.options import BottomSpacedOpt, DefaultOpt, OptionsBase, WarningOpt


class Formatter(object):

    indent = '    '
    not_set = '-- not set --'

    def write(self, single_line, *options):
        options_object = self.get_options(options)
        styles = options_object.map_click()
        single_line = self._indent(single_line, options_object)
        self._write(single_line, options_object, **styles)

    def write_lines(self, lines, options=None):
        lines = lines.splitlines() if isinstance(lines, six.string_types) else lines
        for line in lines:
            self.write(line, options)

    def write_block(self, lines, options=None):
        self.write_lines(lines, options)
        self.separator()

    @classmethod
    def empty_line(cls):
        click.echo()

    def separator(self):
        self.write(70 * '-', WarningOpt, BottomSpacedOpt)

    def display_config(self, config):
        for name, value in six.iteritems(config):
            self.write('{:20}: {}'.format(name, value))
        if not config:
            self.write('No config specified yet.', DefaultOpt(indent=2))

    def format_object(self, dictionary, options):
        options.indent += 1
        for key, value in six.iteritems(dictionary):
            if isinstance(value, dict):
                self.write('{}:'.format(key), options)
                self.format_object(value, options)
            elif isinstance(value, list):
                self._format_list(value, key=key, options=options)
            else:
                self.write('{}: {}'.format(key, value), options)

    def get_options(self, options):
        option_list = list(options) or []
        if option_list and not isinstance(option_list[0], DefaultOpt):
            option_list.insert(0, DefaultOpt)
        return OptionsBase.build_options(option_list)

    def _format_list(self, data_list, key, options):
        # TODO: handle dicts elements in list, maybe even lists in list;
        try:
            value = ', '.join(data_list)
        except TypeError:
            value = data_list
        if not key:
            self.write('{}'.format(value), options)
        else:
            self.write('{}: {}'.format(key, value), options)

    def _write(self, line, options, **styles):
        if options.space_top:
            self.empty_line()

        click.echo(click.style(line, **styles))

        if options.space_bottom:
            self.empty_line()

    def _indent(self, line, options):
        return '{}{}'.format(self.indent * options.indent, line)

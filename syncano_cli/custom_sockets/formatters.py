# -*- coding: utf-8 -*-
import sys

import click
import six
import yaml
from syncano_cli.base.formatters import Formatter
from syncano_cli.base.options import ColorSchema, DefaultOpt, SpacedOpt, TopSpacedOpt, WarningOpt


class SocketFormatter(Formatter):

    SOCKET_LIST_FIELDS = ['name', 'description', 'status', 'status_info', 'endpoints']
    SOCKET_DETAILS_FIELDS = ['config', 'endpoints', 'dependencies', 'metadata']
    ENDPOINT_FIELDS = ['calls', 'acl', 'metadata']

    def display_socket_list(self, socket_list, instance_name):
        if not socket_list:
            self.write('Sockets not defined for `{}` instance.'.format(instance_name),
                       WarningOpt(), SpacedOpt())
            sys.exit(1)
        self.write('Sockets for `{}` instance.'.format(instance_name), SpacedOpt())

        for cs in socket_list:
            lines = self._display_list_details(custom_socket=cs)
            lines.append('See: `{}` {}'.format(
                click.style('syncano sockets details {}'.format(cs.name), fg=ColorSchema.WARNING),
                click.style('for details.', fg=ColorSchema.INFO)
            ))
            self.write_block(lines, DefaultOpt(indent=2))

    @classmethod
    def format_endpoints_list(cls, socket_endpoints):
        yml_dict = {'endpoints': []}
        for endpoint in socket_endpoints:
            endpoint_data = {'name': endpoint.name, 'path': endpoint.links.self}
            endpoint_data.update({'methods': endpoint.allowed_methods})
            yml_dict['endpoints'].append({'endpoint': endpoint_data})
        return yaml.safe_dump(yml_dict, default_flow_style=False)

    def display_socket_details(self, custom_socket, api_key):
        self.write_block(
            [
                'Details for Socket `{}` in `{}` instance.'.format(
                    custom_socket.name,
                    custom_socket.instance_name
                )
            ],
            SpacedOpt()
        )

        lines = self._display_list_details(custom_socket)
        self.write_block(lines)

        for socket_field in self.SOCKET_DETAILS_FIELDS:
            self.display_block(
                socket_field,
                custom_socket,
                base_link=custom_socket.links.links_dict['endpoints'],
                api_key=api_key,
                indent=1,
                skip_fields=['source']
            )

    def display_block(self, block_name, socket, **kwargs):
        handler, kw_names = self.display_handlers[block_name]
        self.write(block_name.capitalize())
        socket_data = getattr(socket, block_name)
        new_kwargs = {key: value for key, value in six.iteritems(kwargs) if key in kw_names}
        handler(socket_data, **new_kwargs)
        self.separator()

    @property
    def display_handlers(self):
        handlers = [
            (self.display_config, ()),
            (self.display_endpoints, ('base_link', 'api_key')),
            (self.format_list, ('indent', 'skip_fields')),
            (self.format_object, 'indent')
        ]
        return dict(zip(self.SOCKET_DETAILS_FIELDS, handlers))

    def _display_list_details(self, custom_socket):
        lines = []
        for field in self.SOCKET_LIST_FIELDS:
            value = getattr(custom_socket, field)
            if field == 'endpoints':
                value = ', '.join(value.keys())
            if not value:
                value = '-- not set --'
            lines.append("{}: {}".format(field.capitalize().replace('_', ' '), value))
        return lines

    def display_endpoints(self, endpoints, base_link, api_key):

        for endpoint_name, endpoint_data in six.iteritems(endpoints):
            self.write('{e_name}:'.format(e_name=endpoint_name, ), DefaultOpt(indent=2), WarningOpt(), TopSpacedOpt())
            self.write('{url_label}: {link}'.format(
                url_label=click.style('URL', fg=ColorSchema.PROMPT),
                link=self._format_link(base_link, endpoint_name, api_key)
            ), DefaultOpt(indent=3))
            self._display_endpoints_fields(endpoint_data)

    @classmethod
    def _format_link(cls, base_link, endpoint_name, api_key):
        instance_part, endpoints_part = base_link.split('endpoints')
        return '{link}'.format(
            link=click.style(
                """{host}{instance_part}
                {endpoints_part}{name}/
                ?api_key={key}""".format(
                    host='https://api.syncano.io',
                    instance_part=instance_part,
                    endpoints_part='endpoints{}'.format(endpoints_part),
                    name=endpoint_name,
                    key=api_key
                ), fg=ColorSchema.INFO
            )
        )

    def _display_endpoints_fields(self, endpoint_data):
        for field in self.ENDPOINT_FIELDS:
            handler_name = '_display_{}'.format(field)
            data = endpoint_data.get(field)
            try:
                handler = getattr(self, handler_name)
            except AttributeError:
                continue
            handler(data, indent=3)

    def _display_calls(self, data, indent):
        if not data:
            self.write('{}: {}'.format('Calls', self.not_set), DefaultOpt(indent=indent))
            return
        self.write(click.style('Calls:', fg=ColorSchema.PROMPT), DefaultOpt(indent=indent))
        for call in data:
            self.format_object(call, indent=indent)

    def _display_acl(self, data, indent):
        if not data:
            self.write('{}: {}'.format(
                click.style('Acl', fg=ColorSchema.PROMPT),
                click.style(self.not_set, fg=ColorSchema.INFO)
            ), DefaultOpt(indent=indent))
            return
        self.write(click.style('Acl:', fg=ColorSchema.PROMPT), DefaultOpt(indent=indent))
        self.format_object(data, DefaultOpt(indent=indent))

    def _display_metadata(self, data, indent):
        if not data:
            self.write('{}: {}'.format(
                click.style('Metadata', fg=ColorSchema.PROMPT),
                click.style(self.not_set, fg=ColorSchema.INFO)
            ), DefaultOpt(indent=indent))
            return
        self.write(click.style('Metadata:', fg=ColorSchema.PROMPT), DefaultOpt(indent=indent))
        self.format_object(data, DefaultOpt(indent=indent))

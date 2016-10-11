# -*- coding: utf-8 -*-
import os
import sys
from collections import defaultdict

import six
import yaml
from syncano_cli.base.formatters import Formatter
from syncano_cli.base.options import DefaultOpt, SpacedOpt, WarningOpt
from syncano_cli.custom_sockets.exceptions import BadYAMLDefinitionInEndpointsException
from syncano_cli.sync.scripts import ALLOWED_RUNTIMES


class DependencyTypeE():
    CLASS = 'class'
    SCRIPT = 'script'


class SocketFormatter(Formatter):

    SOCKET_FIELDS = ['name', 'description', 'endpoints', 'dependencies']
    SOCKET_DISPLAY_FIELDS = ['name', 'description', 'status', 'status_info', 'endpoints']
    HTTP_METHODS = ['GET', 'POST', 'DELETE', 'PUT', 'PATCH']
    ENDPOINT_TYPES = ['script']
    DEPENDENCY_TYPES = {'scripts': DependencyTypeE.SCRIPT, 'classes': DependencyTypeE.CLASS}
    ENDPOINT_FIELDS = ['calls', 'acl', 'metadata']

    @classmethod
    def get_dependency_handlers(cls):
        handlers = {}
        for yml_name, dependency_type in six.iteritems(cls.DEPENDENCY_TYPES):
            handlers[dependency_type] = getattr(cls, 'get_{}_dependency'.format(dependency_type))
        return handlers

    @classmethod
    def to_yml(cls, socket_object):
        """
        A method which transform CustomSocket object from Syncano Python LIB into yml representation.
        :param socket_object: the CustomSocket object;
        :param scope: how many attributes should be processed and showed in output;
        :return: the yml format of the CustomSocket;
        """
        yml_dict = {}
        files = []

        for socket_field in cls.SOCKET_FIELDS:
            if socket_field == 'endpoints':
                yml_dict[socket_field] = cls._yml_process_endpoints(socket_object.endpoints)
            elif socket_field == 'dependencies':
                yml_dict[socket_field], files = cls._yml_process_dependencies(socket_object.dependencies)
            else:
                # TODO: None for skip the description now;
                yml_dict[socket_field] = getattr(socket_object, socket_field, None)

        for meta_name, meta_data in six.iteritems(socket_object.metadata):
            yml_dict[meta_name] = meta_data

        return yaml.safe_dump(yml_dict, default_flow_style=False), files

    @classmethod
    def to_json(cls, socket_yml, directory=None):
        """
        A method which transform yml to the json. This json is used in API call (Syncano Python LIB)
        :param socket_yml: the yml file path;
        :return: the json format of the custom_socket;
        """
        metadata_dict = {}
        api_dict = {}
        for key, value in six.iteritems(socket_yml):
            if key not in cls.SOCKET_FIELDS:
                metadata_dict[key] = value
            else:
                if key == 'endpoints':
                    api_dict[key] = cls._json_process_endpoints(endpoints=value)
                elif key == 'dependencies':
                    api_dict[key] = cls._json_process_dependencies(dependencies=value, directory=directory)
                else:
                    api_dict[key] = value

        api_dict['metadata'] = metadata_dict
        return api_dict

    @classmethod
    def _json_process_endpoints(cls, endpoints):
        api_endpoints = {}

        for name, endpoint_data in six.iteritems(endpoints):
            api_endpoints[name] = {'calls': cls._get_calls(endpoint_data)}
            api_endpoints[name].update({'metadata': cls._get_metadata(endpoint_data)})

        return api_endpoints

    @classmethod
    def _get_metadata(cls, endpoint_data):
        metadata = defaultdict(dict)
        for data_key, data in six.iteritems(endpoint_data):
            if data_key in cls.HTTP_METHODS:
                for metadata_key, inner_data in six.iteritems(data):
                    if metadata_key in cls.ENDPOINT_TYPES:
                        continue
                    if metadata_key == 'parameters':
                        metadata[metadata_key][data_key] = inner_data
                    else:
                        metadata[metadata_key] = inner_data

            elif data_key not in cls.ENDPOINT_TYPES:
                if data_key == 'parameters':
                    metadata[data_key]['*'] = data
                else:
                    metadata[data_key] = data
                metadata[data_key] = data

        return metadata

    @classmethod
    def _get_calls(cls, endpoint_data):
        calls = []
        keys = set(endpoint_data.keys())
        if keys.intersection(set(cls.HTTP_METHODS)) and keys.intersection(set(cls.ENDPOINT_TYPES)):
            raise BadYAMLDefinitionInEndpointsException()

        for type_or_method in keys:
            data = endpoint_data[type_or_method]

            if type_or_method in cls.ENDPOINT_TYPES:
                calls.append({
                    'type': type_or_method,
                    'methods': ['*'],
                    'name': data,
                })

            elif type_or_method in cls.HTTP_METHODS:
                for call_type, name in six.iteritems(data):

                    if call_type in cls.ENDPOINT_TYPES:
                        calls.append({
                            'type': call_type,
                            'methods': [type_or_method],
                            'name': name
                        })
        return calls

    @classmethod
    def _json_process_dependencies(cls, dependencies, directory):
        api_dependencies = []
        dependency_handlers = cls.get_dependency_handlers()
        for dependencies_type, dependency in six.iteritems(dependencies):
            if dependencies_type in cls.DEPENDENCY_TYPES:
                for dependency_name, data in six.iteritems(dependency):
                    dependency_type = cls.DEPENDENCY_TYPES[dependencies_type]
                    base_dependency_data = {
                        'name': dependency_name,
                        'type': dependency_type
                    }
                    typed_dependency_data = dependency_handlers[dependency_type](data, directory=directory)
                    typed_dependency_data.update(base_dependency_data)
                    api_dependencies.append(typed_dependency_data)
        return api_dependencies

    @classmethod
    def get_script_dependency(cls, data, **kwargs):
        """
        Note: when definig new depenency processors use following pattern:
        get_{name}_dependency -> where {name} is one of the defined in DepedencyTypeE
        this allows to easily extend dependency handling;
        :param data:
        :param directory:
        :return:
        """
        directory = kwargs.get('directory')
        return {
            'runtime_name': data['runtime_name'],
            'source': cls._get_source(data['file'], directory),
        }

    @classmethod
    def get_class_dependency(cls, data, **kwargs):
        return {
            'schema': data['schema']
        }

    @classmethod
    def _get_source(cls, file_name, directory):
        with open(os.path.join(directory, '{}'.format(file_name)), 'r+') as source_file:
            return source_file.read()

    @classmethod
    def _yml_process_endpoints(cls, endpoints):
        yml_endpoints = {}
        for endpoint_name, endpoint_data in six.iteritems(endpoints):
            yml_endpoints[endpoint_name] = cls._yml_process_calls(endpoint_data['calls'])
            yml_endpoints.update(cls._yml_process_metadata(endpoint_data))
        return yml_endpoints

    @classmethod
    def _yml_process_metadata(cls, endpoint_data):
        return endpoint_data.get('metadata', {})  # some old Sockets do not have this field;

    @classmethod
    def _yml_process_calls(cls, data_calls):
        calls = {}
        for call in data_calls:
            if call['methods'] == ['*']:
                calls = {call['type']: call['name']}
            else:
                for method in call['methods']:
                    calls.update({method: {call['type']: call['name']}})
        return calls

    @classmethod
    def _yml_process_dependencies(cls, dependencies):
        yml_dependencies = {}
        scripts = {}
        files = []

        for dependency in dependencies:
            if dependency['type'] == 'script':
                file_name = '{name}{ext}'.format(name=dependency['name'],
                                                 ext=ALLOWED_RUNTIMES[dependency['runtime_name']])

                scripts[dependency['name']] = {
                    'runtime_name': dependency['runtime_name'],
                    'file': file_name
                }
                # create file list;
                files.append(
                    {
                        'source': dependency['source'],
                        'file_name': file_name
                    }
                )

        yml_dependencies['scripts'] = scripts

        return yml_dependencies, files

    def display_socket_details(self, custom_socket, api_key):
        self.write('Details for Socket `{}` in `{}` instance.'.format(custom_socket.name,
                                                                      custom_socket.instance_name))
        self.separator()
        self._display_list_details(custom_socket)
        self.separator()
        self.write('Config')
        self.display_config(custom_socket.config)
        self.separator()
        self.write('Endpoints')
        self._display_endpoints(custom_socket.endpoints, base_link=custom_socket.links.links_dict['endpoints'],
                                api_key=api_key)
        self.separator()
        self.write('Metadata')
        self.format_object(custom_socket.metadata, indent=3)
        self.separator()
        self.empty_line()

    def display_socket_list(self, socket_list, instance_name):
        if not socket_list:
            self.write('Sockets not defined for `{}` instance.'.format(instance_name),
                       WarningOpt(), SpacedOpt())
            sys.exit(1)
        self.write('Sockets for `{}` instance.'.format(instance_name), SpacedOpt())

        for cs in socket_list:
            lines = self._display_list_details(custom_socket=cs)
            lines.append('See: `syncano sockets details {}` for details.'.format(cs.name))
            self.write_block(lines, DefaultOpt(indent=2))

    def _display_list_details(self, custom_socket):
        lines = []
        for field in self.SOCKET_DISPLAY_FIELDS:
            value = getattr(custom_socket, field)
            if field == 'endpoints':
                value = ', '.join(value.keys())
            if not value:
                value = '-- not set --'
            lines.append("{}: {}".format(field.capitalize().replace('_', ' '), value))
        return lines

    def _display_endpoints(self, endpoints, base_link, api_key):
        for endpoint_name, endpoint_data in six.iteritems(endpoints):
            self.write('{e_name}:'.format(e_name=endpoint_name, ), DefaultOpt(indent=2))
            self.write('URL: {host}{base_link}{name}/?api_key={key}'.format(
                host='https://api.syncano.io',
                base_link=base_link,
                name=endpoint_name,
                key=api_key
            ), DefaultOpt(indent=3))
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
        self.write('Calls:', DefaultOpt(indent=indent))
        for call in data:
            self.format_object(call, indent=indent)

    def _display_acl(self, data, indent):
        if not data:
            self.write('{}: {}'.format('Acl', self.not_set), DefaultOpt(indent=indent))
            return
        self.write('ACL:', DefaultOpt(indent=indent))
        self.format_object(data, DefaultOpt(indent=indent))

    def _display_metadata(self, data, indent):
        if not data:
            self.write('{}: {}'.format('Metadata', self.not_set), DefaultOpt(indent=indent))
            return
        self.write('Metadata:', DefaultOpt(indent=indent))
        self.format_object(data, DefaultOpt(indent=indent))

    @classmethod
    def format_endpoints_list(cls, socket_endpoints):
        yml_dict = {'endpoints': []}
        for endpoint in socket_endpoints:
            endpoint_data = {'name': endpoint.name, 'path': endpoint.links.self}
            endpoint_data.update({'methods': endpoint.allowed_methods})
            yml_dict['endpoints'].append({'endpoint': endpoint_data})
        return yaml.safe_dump(yml_dict, default_flow_style=False)

# -*- coding: utf-8 -*-
import json
import os
from collections import defaultdict

import six
import yaml
from syncano_cli.custom_sockets.exceptions import BadYAMLDefinitionInEndpointsException
from syncano_cli.sync.scripts import ALLOWED_RUNTIMES


class SocketFormatter(object):

    SOCKET_FIELDS = ['name', 'description', 'endpoints', 'dependencies']
    HTTP_METHODS = ['GET', 'POST', 'DELETE', 'PUT', 'PATCH']
    ENDPOINT_TYPES = ['script']
    DEPENDENCY_TYPES = {'scripts': 'script'}

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
    def _process_response_example(cls, metadata_key, inner_data):
        if metadata_key not in cls.ENDPOINT_TYPES:
            if metadata_key == 'response':
                if 'example' in inner_data:
                    if isinstance(inner_data, dict):
                        inner_data['example'] = inner_data
                    if isinstance(inner_data, six.string_types):
                        try:
                            inner_data['example'] = json.loads(inner_data['example'])
                        except (TypeError, ValueError):
                            inner_data['example'] = inner_data['example']

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
                        cls._process_response_example(metadata_key, inner_data)
                        metadata[metadata_key] = inner_data

            elif data_key not in cls.ENDPOINT_TYPES:
                if data_key == 'parameters':
                    metadata[data_key]['*'] = data
                else:
                    cls._process_response_example(data_key, data)
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

        for dependencies_type, dependency in six.iteritems(dependencies):
            if dependencies_type in cls.DEPENDENCY_TYPES:
                for dependency_name, data in six.iteritems(dependency):
                    api_dependencies.append({
                        'type': cls.DEPENDENCY_TYPES[dependencies_type],
                        'runtime_name': data['runtime_name'],
                        'name': dependency_name,
                        'source': cls._get_source(data['file'], directory),
                    })
        return api_dependencies

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
        return endpoint_data['metadata']

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

    @classmethod
    def format_socket_details(cls, cs):
        yml_content, files = cls.to_yml(cs)
        return yml_content

    @classmethod
    def format_socket_list(cls, socket_list):
        yml_dict = {'sockets': []}
        for cs in socket_list:
            yml_dict['sockets'].append(
                {
                    'socket': {
                        'name': cs.name,
                        'status': cs.status,
                        'info': cs.status_info
                    }
                }
            )
        return yaml.safe_dump(yml_dict, default_flow_style=False)

    @classmethod
    def format_endpoints_list(cls, socket_endpoints):
        yml_dict = {'endpoints': []}
        for endpoint in socket_endpoints:
            endpoint_data = {'name': endpoint.name, 'path': endpoint.links.self}
            endpoint_data.update({'methods': endpoint.allowed_methods})
            yml_dict['endpoints'].append({'endpoint': endpoint_data})
        return yaml.safe_dump(yml_dict, default_flow_style=False)

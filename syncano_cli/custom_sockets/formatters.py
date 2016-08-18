import os

import click
import six
import sys


class SocketScopeFormat(object):
    ALL = 'all'
    DEPENDENCIES = 'dependencies'
    ENDPOINTS = 'endpoints'


class SocketFormatter(object):

    SOCKET_NAMES = ['name', 'description', 'endpoints', 'dependencies']
    HTTP_METHODS = ['GET', 'POST', 'DELETE', 'PUT', 'PATCH']
    ENDPOINT_TYPES = ['script']
    DEPENDENCY_TYPES = {'scripts': 'script'}

    @classmethod
    def to_yml(cls, socket_object, scope=SocketScopeFormat.ALL):
        """
        A method which transform CustomSocket object from Syncano Python LIB into yml representation.
        :param socket_object: the CustomSocket object;
        :param scope: how many attributes should be processed and showed in output;
        :return: the yml format of the CustomSocket;
        """
        pass

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
            if key not in cls.SOCKET_NAMES:
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

        for endpoint in endpoints:
            for name, endpoint_data in six.iteritems(endpoint):
                api_endpoints[name] = {'calls': cls._get_calls(endpoint_data)}

        return api_endpoints

    @classmethod
    def _get_calls(cls, endpoint_data):
        calls = []
        keys = set(endpoint_data.keys())
        if keys.intersection(set(cls.HTTP_METHODS)) and keys.intersection(set(cls.ENDPOINT_TYPES)):
            click.echo("ERROR: Specify one general endpoint or specify endpoints for each method.")
            sys.exit(1)

        for type_or_method in keys:
            data = endpoint_data[type_or_method]

            if type_or_method in cls.ENDPOINT_TYPES:
                calls.append({
                    'type': type_or_method,
                    'methods': ['*'],
                    'name': data,
                })

            elif type_or_method in cls.HTTP_METHODS:
                if len(data) != 1:
                    click.echo("ERROR: Only one endpoint per method allowed.")
                    sys.exit(1)

                for call_type, name in six.iteritems(data):
                    calls.append({
                        'type': call_type,
                        'methods': [type_or_method],
                        'name': name
                    })

        return calls

    @classmethod
    def _json_process_dependencies(cls, dependencies, directory):
        api_dependencies = []

        for dependencies_types in dependencies:
            for dependency_type, data in six.iteritems(dependencies_types):
                if dependency_type in cls.DEPENDENCY_TYPES:
                    for dependency in data:
                        for name, dependency_data in six.iteritems(dependency):
                            api_dependencies.append({
                                'type': cls.DEPENDENCY_TYPES[dependency_type],
                                'runtime_name': dependency_data['runtime_name'],
                                'name': name,
                                'source': cls._get_source(dependency_data['file'], directory)
                            })
        return api_dependencies

    @classmethod
    def _get_source(cls, file_name, directory):
        with open(os.path.join(directory, 'scripts/{}'.format(file_name)), 'r+') as source_file:
            return source_file.read()

    @classmethod
    def format_socket_details(cls, cs):
        details_sting = ""
        fields = [
            'name', 'endpoints', 'dependencies', 'metadata',
            'status', 'status_info', 'created_at', 'updated_at'
        ]

        formatter_map = {
            'default': cls._default_formatter,
            'endpoints': cls._endpoints_formatter,
            'dependencies': cls._dependencies_formatter
        }

        for field_name in fields:
            formatter = formatter_map.get(field_name, formatter_map['default'])
            details_sting += "{label:>29}: {value}\n".format(
                label=field_name.replace('_', ' '),
                value=formatter(getattr(cs, field_name))
            )
        return details_sting

    @classmethod
    def _endpoints_formatter(cls, endpoints):

        def format_calls(calls):
            details_string = ""
            for call in calls:
                for label, value in six.iteritems(call):
                    details_string += "\n{label:>55}: {value}".format(label=label, value=value)
                details_string += '\n'
            return details_string

        details_string = "\n"
        for endpoint_name, endpoint_data in six.iteritems(endpoints):
            details_string += "{name:>43}: {calls}\n".format(name=endpoint_name,
                                                             calls=format_calls(endpoint_data['calls']))
        return details_string

    @classmethod
    def _dependencies_formatter(cls, dependencies):
        details_string = ""
        for dependency in dependencies:
            for label, value in six.iteritems(dependency):
                details_string += "\n{label:>55}: {value}".format(label=label, value=value.strip())
            details_string += '\n'
        return details_string

    @classmethod
    def _default_formatter(cls, value):
        return value

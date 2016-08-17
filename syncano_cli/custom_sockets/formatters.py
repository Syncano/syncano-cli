import six


class SocketFormatter(object):

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

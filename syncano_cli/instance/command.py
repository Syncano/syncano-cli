# -*- coding: utf-8 -*-
import six
from syncano_cli.base.command import BaseConnectionCommand
from syncano_cli.config import ACCOUNT_CONFIG

if six.PY2:
    from ConfigParser import NoOptionError
elif six.PY3:
    from configparser import NoOptionError
else:
    raise ImportError()


class InstanceCommands(BaseConnectionCommand):

    def list(self):
        try:
            default_instance_name = ACCOUNT_CONFIG.get('DEFAULT', 'instance_name')
        except NoOptionError:
            default_instance_name = None

        return self.format_list(self.connection.Instance.please.all(), default_instance_name)

    def details(self, instance_name):
        return self.format_details(self.connection.Instance.please.get(name=instance_name))

    def delete(self, instance_name):
        self.connection.Instance.please.delete(name=instance_name)

    @classmethod
    def set_default(cls, instance_name, config_path):
        ACCOUNT_CONFIG.set('DEFAULT', 'instance_name', instance_name)
        with open(config_path, 'wt') as fp:
            ACCOUNT_CONFIG.write(fp)

    def create(self, instance_name, description=None):
        kwargs = {
            'name': instance_name
        }
        if description:
            kwargs.update({'description': description})
        self.connection.Instance.please.create(**kwargs)

    @classmethod
    def format_details(cls, instance):
        details_template = """Name: {instance.name}
Description: {description}
Owner: {instance.owner.email}
Metadata: {instance.metadata}"""

        return details_template.format(instance=instance, description=instance.description or u'N/A')

    @classmethod
    def format_list(cls, instances, default_instance_name):
        list_template = """Available Instances:{}"""
        lines = ''

        def get_name_label(name, default_instance_name):
            if instance.name != default_instance_name:
                return u"{}".format(name)
            return u"{} (default)".format(name)

        for instance in instances:
            lines += u"\n\t- {name}: {description}".format(
                description=instance.description or u'no description',
                name=get_name_label(instance.name, default_instance_name)
            )

        return list_template.format(lines)

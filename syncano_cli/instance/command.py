# -*- coding: utf-8 -*-
import click
from syncano_cli.base.command import BaseCommand
from syncano_cli.base.options import BottomSpacedOpt, ColorSchema, SpacedOpt, TopSpacedOpt, WarningOpt


class InstanceCommands(BaseCommand):

    def list(self):
        return self.api_list()

    def api_list(self):
        return self.connection.Instance.please.all()

    def details(self, instance_name):
        return self.display_details(self.connection.Instance.please.get(name=instance_name))

    def delete(self, instance_name):
        self.connection.Instance.please.delete(name=instance_name)
        self.formatter.write('Instance `{}` deleted.'.format(instance_name), WarningOpt(), SpacedOpt())

    def set_default(self, instance_name):
        self.config.set_config('DEFAULT', 'instance_name', instance_name)
        self.config.write_config()

    def create(self, instance_name, description=None):
        kwargs = {
            'name': instance_name
        }
        if description:
            kwargs.update({'description': description})
        instance = self.connection.Instance.please.create(**kwargs)
        self.formatter.write('Instance `{}` created.'.format(instance.name), TopSpacedOpt())
        self.formatter.write('To set this instance as default use: `syncano instances default {}`'.format(
            instance.name
        ), BottomSpacedOpt())
        return instance

    def display_details(self, instance):
        self.formatter.write('Details for Instance `{}`.'.format(instance.name), SpacedOpt())

        details_template = """Name: {instance.name}
Description: {description}
Owner: {instance.owner.email}
Metadata: {instance.metadata}

"""

        self.formatter.write_lines(
            details_template.format(instance=instance, description=instance.description or u'N/A').splitlines())

    def display_list(self, instances):
        default_instance_name = self.config.get_config('DEFAULT', 'instance_name')

        self.formatter.write("Available Instances:", SpacedOpt())

        def get_name_label(name, default_instance_name):
            if instance.name != default_instance_name:
                return u"{}".format(name)
            return click.style(u"{} (default)".format(name), fg=ColorSchema.WARNING)

        for instance in instances:
            self.formatter.write(u"* {name}: {description}".format(
                description=click.style(instance.description or u'no description', fg=ColorSchema.INFO),
                name=get_name_label(instance.name, default_instance_name)
            ))
        self.formatter.empty_line()

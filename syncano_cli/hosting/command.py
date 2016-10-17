# -*- coding: utf-8 -*-
import os
import sys
from collections import namedtuple

import click
import six
from syncano_cli.base.command import BaseInstanceCommand
from syncano_cli.base.options import BottomSpacedOpt, ColorSchema, PromptOpt, SpacedOpt, TopSpacedOpt, WarningOpt
from syncano_cli.hosting.exceptions import NoHostingFoundException, PathNotFoundException
from syncano_cli.hosting.utils import slugify


class HostingCommands(BaseInstanceCommand):

    COMMAND_CONFIG = {
        'hosting': [
            {
                'name': 'domain',
                'required': True,
                'info': '',
                'default': 'default'
            },
            {
                'name': 'project_dir',
                'required': False,
                'info': '',
                'default': ''
            },
            {
                'name': 'instance_name',
                'required': True,
                'info': '',
                'default': ''
            },
        ]
    }
    COMMAND_SECTION = 'HOSTING'
    COMMAND_CONFIG_PATH = '.hosting-syncano'  # local dir (this one in which command is executed)

    def setup_command_config(self, config_path):
        project_dir = os.getcwd()
        self.formatter.write('Setup your Hosting. Your working directory is: {}'.format(
            project_dir
        ), SpacedOpt())
        current_dir = os.path.split(project_dir)[1].decode('utf-8')
        domain = slugify(current_dir)
        instance_name = self.config.get_config('DEFAULT', 'instance_name')

        defaults = {
            'instance_name': instance_name,
            'project_dir': project_dir,
            'domain': domain
        }
        config = {}

        for config_meta in self.COMMAND_CONFIG.get(self.COMMAND_SECTION.lower()):
            var_name = config_meta['name']
            required = config_meta['required']
            default = defaults.get(var_name) or config_meta['default']
            if required and not self.config.has_option(self.COMMAND_SECTION, var_name, config='local'):
                config[var_name] = self.prompter.prompt(var_name, default=default)

        self.config.add_section(self.COMMAND_SECTION, config='local')
        for config_name, config_val in six.iteritems(config):
            self.config.set_config(self.COMMAND_SECTION, config_name, config_val, config='local')

        self.config.write_config(config='local')

        # add project to global config (summary command);
        self.config.update_info_about_projects(project_dir)

    def list_hostings(self):
        return [
            (hosting.label, hosting.domains) for hosting in self.instance.hostings.all()
        ]

    def print_hostings(self, hostings):
        if not hostings:
            self.formatter.write('No Hosting defined for instance `{}`.'.format(
                self.instance.name
            ), SpacedOpt())
            sys.exit(1)
        self.formatter.write('Hosting defined in Instance `{}`:'.format(self.instance.name), SpacedOpt())
        self.formatter.write('{0:30}{1:20}{2:20}'.format('Label', 'Domains', 'URL'), PromptOpt())

        Domain = namedtuple('Domain', ['domain', 'url'])
        for label, domains in hostings:
            domain_url = [Domain(domain, self.get_hosting_url(domain)) for domain in domains]
            self.formatter.write(
                '{0:30}{1:20}{2:20}'.format(
                    label,
                    domain_url[0].domain if domain_url else '',
                    domain_url[0].url if domain_url else '')
            )
            if domain_url[1:]:
                for domain_url in domain_url[1:]:
                    self.formatter.write(
                        '{0:30}{1:20}{2:20}'.format('', domain_url.domain, domain_url.url)
                    )
        self.formatter.empty_line()

    def list_hosting_files(self, domain):
        hosting = self._get_hosting(domain=domain)
        files_list = hosting.list_files()
        return files_list

    def publish(self, domain, base_dir):
        self.formatter.write('Your site is publishing.', SpacedOpt())
        uploaded_files = []
        hosting = self._get_hosting(domain=domain, is_new=True)
        upload_method_name = 'update_file'
        if not hosting:
            # create a new Hosting Socket if no default is present;
            hosting = self.create_hosting(label='{} Hosting Socket'.format(
                domain.capitalize()
            ), domain=domain)
            upload_method_name = 'upload_file'

        for folder, subs, files in os.walk(base_dir):
            path = folder.split(base_dir)[1]

            if path.startswith('/') or path.startswith('\\'):  # skip the /
                path = path[1:]

            for single_file in files:
                if path:
                    file_path = '{}/{}'.format(path, single_file)
                else:
                    file_path = single_file

                sys_path = os.path.join(folder, single_file)
                with open(sys_path, 'rb') as upload_file:
                    self.formatter.write('* Uploading file: {}'.format(click.style(file_path,
                                                                                   fg=ColorSchema.WARNING)))
                    getattr(hosting, upload_method_name)(path=file_path, file=upload_file)

                uploaded_files.append(file_path)
        return uploaded_files

    def delete_hosting(self, domain):
        hosting = self._get_hosting(domain=domain)
        deleted_label = hosting.label
        hosting.delete()
        self.formatter.write('Hosting `{}` deleted.'.format(deleted_label), SpacedOpt())

    def delete_path(self, domain, path=None):
        hosting = self._get_hosting(domain=domain)
        hosting_files = hosting.list_files()

        for hosting_file in hosting_files:
            if hosting_file.path == path:
                hosting_file.delete()
                click.echo('INFO: File `{}` deleted.'.format(path))
                return
        raise PathNotFoundException(format_args=[path])

    def update_single_file(self, domain, path, file):
        hosting = self._get_hosting(domain=domain)
        hosting.update_file(path, file)
        self.formatter.write('File `{}` updated.'.format(path), SpacedOpt())

    def create_hosting(self, label, domain):
        hosting = self.instance.hostings.create(
            label=label,
            domains=[domain]
        )
        return hosting

    def _get_hosting(self, domain, is_new=False):
        hostings = self.instance.hostings.all()
        to_return = None

        for hosting in hostings:
            if domain in hosting.domains:
                to_return = hosting
                break

        if not to_return and not is_new:
            raise NoHostingFoundException(format_args=[domain])
        return to_return

    def print_hosting_files(self, domain, hosting_files):
        self.formatter.write('Hosting files for domain `{}` in instance `{}`:'.format(domain, self.instance.name),
                             TopSpacedOpt())
        self.formatter.write(self.get_hosting_url(domain), BottomSpacedOpt())

        self.formatter.separator()
        for hosting_file in hosting_files:
            self.formatter.write('* {}'.format(hosting_file.path), WarningOpt())
        self.formatter.empty_line()

    def get_hosting_url(self, domain):
        if domain == 'default':
            link = click.style(
                'https://{instance_name}.syncano.site'.format(
                    instance_name=self.instance.name,
                ), fg=ColorSchema.WARNING)
        else:
            link = click.style(
                'https://{instance_name}--{domain}.syncano.site'.format(
                    instance_name=self.instance.name,
                    domain=domain
                ), fg=ColorSchema.WARNING)
        return link

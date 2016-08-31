# -*- coding: utf-8 -*-
import os
import sys

import click


class HostingCommands(object):

    def __init__(self, instance):
        self.instance = instance

    def list_hosting(self):
        return [
            (hosting.label, hosting.domains) for hosting in self.instance.hostings.all()
        ]

    def list_hosting_files(self, domain):
        hosting = self._get_hosting(domain=domain)
        files_list = hosting.list_files()
        return files_list

    def publish(self, domain, base_dir):
        uploaded_files = []
        hosting = self._get_hosting(domain=domain, is_new=True)
        upload_method_name = 'update_file'
        if not hosting:
            # create a new hosting if no default is present;
            hosting = self.create_hosting(label='Default hosting', domain=domain)
            upload_method_name = 'upload_file'

        for folder, subs, files in os.walk(base_dir):
            path = folder.split(base_dir)[1]

            if path.startswith('/'):  # skip the /
                path = path[1:]

            for single_file in files:
                if path:
                    file_path = '{}/{}'.format(path, single_file)
                else:
                    file_path = single_file

                self._validate_path(file_path)

                sys_path = os.path.join(folder, single_file)
                with open(sys_path, 'rb') as upload_file:
                    click.echo(u'INFO: Uploading file: {}'.format(file_path))
                    getattr(hosting, upload_method_name)(path=file_path, file=upload_file)

                uploaded_files.append(file_path)
        return uploaded_files

    def unpublish(self, domain):
        hosting = self._get_hosting(domain=domain)
        hosting.domains = ['unpublished']
        hosting.save()
        click.echo('INFO: Hosting `{}` unpublished.'.format(hosting.label))

    def delete_hosting(self, domain, path=None):
        hosting = self._get_hosting(domain=domain)
        deleted_label = hosting.label
        hosting.delete()
        click.echo('INFO: Hosting `{}` deleted.'.format(deleted_label))

    def delete_path(self, domain, path=None):
        hosting = self._get_hosting(domain=domain)
        hosting_files = hosting.list_files()
        is_deleted = False
        for hosting_file in hosting_files:
            if hosting_file.path == path:
                is_deleted = True
                hosting_file.delete()
                break

        if is_deleted:
            click.echo('INFO: File `{}` deleted.'.format(path))
            sys.exit(1)
        click.echo('INFO: File `{}` not found.'.format(path))

    def update_single_file(self, domain, path, file):
        hosting = self._get_hosting(domain=domain)
        hosting.update_file(path, file)
        click.echo('INFO: File `{}` updated.'.format(path))

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
            click.echo(u'WARN: No default hosting found. Exit.')
            sys.exit(1)

        return to_return

    def _validate_path(self, file_path):
        try:
            file_path.decode('ascii')
        except UnicodeEncodeError:
            click.echo(u'ERROR: Unicode characters in path are not supported. Check the files names.')
            sys.exit(1)

    def print_hosting_files(self, hosting_files):
        print('Hosting files:')
        self._print_separator()
        for hosting_file in hosting_files:
            print(hosting_file.path)

    @staticmethod
    def _print_separator():
        print(79 * '-')

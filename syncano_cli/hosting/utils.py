# -*- coding: utf-8 -*-
import os
import sys
import time

from syncano_cli.logger import get_logger

LOG = get_logger('syncano-hosting')


class HostingCommands(object):

    def __init__(self, instance):
        self.instance = instance

    def list_hosting(self):
        return [
            (hosting.label, hosting.domains) for hosting in self.instance.hostings.all()
        ]

    def list_hosting_files(self, domain):
        hosting = self._get_hosting(domain=domain)
        if not hosting:
            LOG.warn('No default hosting found. Exit.')
            sys.exit(1)

        files_list = hosting.list_files()
        return files_list

    def publish(self, domain, base_dir):
        uploaded_files = []
        hosting = self._get_hosting(domain=domain)
        if not hosting:
            # create a new hosting if no default is present;
            hosting = self.create_hosting(label='Default hosting', domain=domain)

        for folder, subs, files in os.walk(base_dir):
            path = folder.split(base_dir)[1][1:]  # skip the /
            for single_file in files:
                if path:
                    file_path = '{}/{}'.format(path, single_file)
                else:
                    file_path = single_file

                sys_path = os.path.join(folder, single_file)
                with open(sys_path, 'rb') as upload_file:
                    LOG.info('Uploading file: {}'.format(file_path))
                    hosting.upload_file(path=file_path, file=upload_file)

                uploaded_files.append(file_path)
                time.sleep(1)  # avoid throttling;
        return uploaded_files

    def create_hosting(self, label, domain):
        hosting = self.instance.hostings.create(
            label=label,
            domains=[domain]
        )
        return hosting

    def _get_hosting(self, domain):
        hostings = self.instance.hostings.all()
        for hosting in hostings:
            if domain in hosting.domains:
                return hosting

    def print_hosting_files(self, hosting_files):
        print('Hosting files:')
        self._print_separator()
        for file_path in hosting_files:
            print(file_path)

    @staticmethod
    def _print_separator():
        print(79 * '-')

# -*- coding: utf-8 -*-
import os
import time


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
        hosting = self._get_hosting(domain=domain)
        for folder, subs, files in os.walk(base_dir):
            path = folder.split(base_dir)[1][1:]  # skip the /
            for single_file in files:
                if path:
                    file_path = '{}/{}'.format(path, single_file)
                else:
                    file_path = single_file

                sys_path = os.path.join(folder, single_file)
                with open(sys_path, 'rb') as upload_file:
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

    def print_hostng_created_info(self, created_hosting):
        print('{label:30}{domains}'.format(label=created_hosting.label, domains=created_hosting.domains))

    def _get_hosting(self, domain):
        hostings = self.instance.hostings.all()
        for hosting in hostings:
            if domain in hosting.domains:
                return hosting

    def print_hosting_list(self, hosting_list):
        print('Label: Domains')
        self._print_separator()
        for label, domains in hosting_list:
            print('{label:30}{domains}'.format(label=label, domains=domains))

    def print_hosting_files(self, hosting_files):
        print('Hosting files:')
        self._print_separator()
        for file_path in hosting_files:
            print(file_path)

    @staticmethod
    def _print_separator():
        print(79 * '-')

# -*- coding: utf-8 -*-
import json
import os
import subprocess
import yaml

import click
from syncano.models import CustomSocket, SocketEndpoint
from syncano_cli.custom_sockets.formatters import SocketFormatter


class SocketCommand(object):

    list_line_template = '{socket_name:^29}|{socket_status:^19}|{status_info:^29}'
    socket_line_template = '{endpoint_name:^39}|{calls:^40}'
    TEMPLATE_DIR = 'custom_sockets/template/'
    SOCKET_FILE_NAME = 'socket.yml'

    def __init__(self, instance):
        self.instance = instance

    def list(self):
        # TODO: move the presentation logic to formatter;
        click.echo(self.list_line_template.format(
            socket_name='socket name',
            socket_status='status',
            status_info='status info',
        ))
        click.echo(80 * '-')
        for cs in CustomSocket.please.all(instance_name=self.instance.name):
            click.echo(self.list_line_template.format(
                socket_name=cs.name,
                socket_status=cs.status,
                status_info=cs.status_info
            ))

    def details(self, socket_name):
        cs = CustomSocket.please.get(name=socket_name, instance_name=self.instance.name)
        click.echo(SocketFormatter.format_socket_details(cs))

    def list_endpoints(self):
        # TODO: move the presentation logic to formatter;
        click.echo(self.socket_line_template.format(endpoint_name='Name', calls='Calls'))
        click.echo(80 * '-')
        endpoints = SocketEndpoint.get_all_endpoints(instance_name=self.instance.name)
        for endpoint in endpoints:
            click.echo(self.socket_line_template.format(endpoint_name=endpoint.name, calls=endpoint.calls))

    def delete(self, socket_name):
        print('delete {}'.format(socket_name))

    def publish_from_dir(self, dir_path):
        with open(os.path.join(dir_path, self.SOCKET_FILE_NAME)) as socket_file:
            yml_file = yaml.safe_load(socket_file)

        api_data = SocketFormatter.to_json(socket_yml=yml_file, directory=dir_path)
        api_data.update({'instance_name': self.instance.name})
        custom_socket = CustomSocket.please.create(**api_data)
        print(custom_socket.status)

    def publish_from_url(self, ulr_path):
        print('url publish')

    def create_template(self, socket_name, destination):
        print('template {}'.format(destination))

    def create_template_from_local_template(self, destination):

        if not os.path.isdir(destination):
            os.makedirs(destination)

        for roots, dirs, files in os.walk(self.TEMPLATE_DIR):
            for dir_name in dirs:
                if not os.path.isdir(os.path.join(destination, dir_name)):
                    os.makedirs(os.path.join(destination, dir_name))

            for file_name in files:
                try:
                    directory = roots.split(self.TEMPLATE_DIR)[1]
                except IndexError:
                    directory = ''
                with open(os.path.join(roots, file_name), 'r+') as file_to_read:
                    with open(os.path.join("{}/{}".format(destination, directory) if directory else destination,
                                           file_name), 'w+') as file_to_write:
                        file_to_write.write(file_to_read.read())

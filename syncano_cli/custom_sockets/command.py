# -*- coding: utf-8 -*-

import os

import click
import six
import yaml
from syncano.models import CustomSocket, SocketEndpoint
from syncano_cli.custom_sockets.formatters import SocketFormatter
from syncano_cli.custom_sockets.templates.socket_template import SCRIPTS, SOCKET_YML


class SocketCommand(object):

    SOCKET_FILE_NAME = 'socket.yml'

    def __init__(self, instance):
        self.instance = instance

    def list(self):
        sockets = [cs for cs in CustomSocket.please.all(instance_name=self.instance.name)]
        click.echo(SocketFormatter.format_socket_list(socket_list=sockets))

    def details(self, socket_name):
        cs = CustomSocket.please.get(name=socket_name, instance_name=self.instance.name)
        click.echo(SocketFormatter.format_socket_details(cs))

    def list_endpoints(self):
        endpoints = SocketEndpoint.get_all_endpoints(instance_name=self.instance.name)
        click.echo(SocketFormatter.format_endpoints_list(socket_endpoints=endpoints))

    def delete(self, socket_name):
        custom_socket = CustomSocket.please.get(name=socket_name, instance_name=self.instance.name)
        custom_socket.delete()
        click.echo("INFO: Custom Socket {} delted.".format(socket_name))

    def install_from_dir(self, dir_path):
        with open(os.path.join(dir_path, self.SOCKET_FILE_NAME)) as socket_file:
            yml_file = yaml.safe_load(socket_file)

        api_data = SocketFormatter.to_json(socket_yml=yml_file, directory=dir_path)
        api_data.update({'instance_name': self.instance.name})
        custom_socket = CustomSocket.please.create(**api_data)
        click.echo('INFO: socket {} created.'.format(custom_socket.name))

    def install_from_url(self, url_path, name):
        CustomSocket(name=name).install_from_url(url=url_path, instance_name=self.instance.name)
        click.echo('INFO: Installing socket from url: do `syncano sockets list` to obtain the status.')

    def run(self, endpoint_name, method='GET', data=None):
        endpoints = SocketEndpoint.get_all_endpoints(instance_name=self.instance.name)
        run_endpoint = None
        for endpoint in endpoints:
            if endpoint.name == endpoint_name:
                run_endpoint = endpoint
                break

        if not run_endpoint:
            click.echo("ERROR: endpoint not found")
        return run_endpoint.run(method=method, data=data or {})

    def create_template(self, socket_name, destination):

        if not os.path.isdir(destination):
            os.makedirs(destination)

        if not os.path.isdir(os.path.join(destination, 'scripts')):
            os.makedirs(os.path.join(destination, 'scripts'))

        socket = CustomSocket.please.get(name=socket_name, instance_name=self.instance.name)

        yml_file, scripts = SocketFormatter.to_yml(socket_object=socket)

        with open(os.path.join(destination, 'socket.yml'), 'w+') as socket_yml:
            socket_yml.write(yml_file)

        for file_meta in scripts:
            with open(os.path.join(destination, 'scripts/{}'.format(file_meta['file_name'])), 'w+') as script_file:
                script_file.write(file_meta['source'])
        click.echo('INFO: template created in {}.'.format(destination))

    def create_template_from_local_template(self, destination):
        if not os.path.isdir(destination):
            os.makedirs(destination)

        if not os.path.isdir(os.path.join(destination, 'scripts')):
            os.makedirs(os.path.join(destination, 'scripts'))

        with open(os.path.join(destination, 'socket.yml'), 'w+') as socket_yml:
            socket_yml.write(SOCKET_YML)

        for script_name, script_source in six.iteritems(SCRIPTS):
            with open(os.path.join(destination, script_name), 'w+') as script_file:
                script_file.write(script_source)

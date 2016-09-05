# -*- coding: utf-8 -*-

import os
from yaml.parser import ParserError

import click
import requests
import six
import yaml

import sys
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
        click.echo("INFO: Custom Socket {} deleted.".format(socket_name))

    def install_from_dir(self, dir_path):

        with open(os.path.join(dir_path, self.SOCKET_FILE_NAME)) as socket_file:
            yml_file = yaml.safe_load(socket_file)

        self.set_up_config(yml_file)

        api_data = SocketFormatter.to_json(socket_yml=yml_file, directory=dir_path)
        api_data.update({'instance_name': self.instance.name})
        custom_socket = CustomSocket.please.create(**api_data)
        click.echo('INFO: socket {} created.'.format(custom_socket.name))

    def install_from_url(self, url_path, name):
        socket_yml = self.fetch_file(url_path)
        self.set_up_config(socket_yml)

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

    def set_up_config(self, socket_yml):
        config = socket_yml['config']
        instance_config = self.instance.get_config()

        for config_var in config:
            config_var_name = config_var['name']

            if config_var_name not in instance_config:
                prompt_str = 'Provide value for {}'.format(config_var_name)
                if config_var.get('description', None):
                    prompt_str = '{} ({})'.format(prompt_str, config_var['description'])
                config_var_value = click.prompt(prompt_str)
                instance_config[config_var_name] = config_var_value

        self.instance.set_config(instance_config)

    def fetch_file(self, url_path):
        response = requests.get(url_path)
        if response.status_code == 200:
            try:
                return yaml.safe_load(response.text)
            except ParserError:
                click.echo("ERROR: Can't parse yml file.")
                sys.exit(1)

        click.echo("ERROR: Can't fetch the file: {}.".format(url_path))
        sys.exit(1)

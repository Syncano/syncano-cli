# -*- coding: utf-8 -*-

import os

import click
import requests
import six
import yaml
from syncano.exceptions import SyncanoRequestError
from syncano.models import CustomSocket, SocketEndpoint
from syncano_cli.base.command import BaseCommand
from syncano_cli.base.options import BottomSpacedOpt, SpacedOpt, TopSpacedOpt
from syncano_cli.custom_sockets.exceptions import (
    EndpointNotFoundException,
    SocketAPIException,
    SocketFileFetchException,
    SocketYMLParseException
)
from syncano_cli.custom_sockets.formatters import SocketFormatter
from syncano_cli.custom_sockets.jsonyaml import SocketJsonYml
from syncano_cli.custom_sockets.parsers import SocketConfigParser
from syncano_cli.custom_sockets.templates.socket_template import SCRIPTS, SOCKET_YML
from yaml.parser import ParserError


class SocketCommand(BaseCommand):

    SOCKET_FILE_NAME = 'socket.yml'

    def __init__(self, config):
        super(SocketCommand, self).__init__(config)
        self.socket_formatter = SocketFormatter()
        self.socket_processor = SocketJsonYml()

    def list(self):
        sockets = [cs for cs in CustomSocket.please.all(instance_name=self.instance.name)]
        self.socket_formatter.display_socket_list(socket_list=sockets, instance_name=self.instance.name)

    def details(self, socket_name):
        cs = CustomSocket.please.get(name=socket_name, instance_name=self.instance.name)
        self.socket_formatter.display_socket_details(cs, self.connection.connection().api_key)

    def recheck(self, socket_name):
        cs = CustomSocket.please.get(name=socket_name, instance_name=self.instance.name)
        cs.recheck()

    def get_config(self, socket_name):
        cs = CustomSocket.please.get(name=socket_name, instance_name=self.instance.name)
        self.formatter.write('Config for Socket `{}`'.format(cs.name), TopSpacedOpt())
        self.formatter.display_config(cs.config)

    def list_endpoints(self):
        endpoints = SocketEndpoint.get_all_endpoints(instance_name=self.instance.name)
        self.socket_formatter.display_all_endpoints(endpoints=endpoints, api_key=self.connection.connection().api_key)

    def delete(self, socket_name):
        custom_socket = CustomSocket.please.get(name=socket_name, instance_name=self.instance.name)
        custom_socket.delete()
        click.echo("INFO: Sockets {} deleted.".format(socket_name))

    def install_from_dir(self, dir_path):

        with open(os.path.join(dir_path, self.SOCKET_FILE_NAME)) as socket_file:
            yml_file = yaml.safe_load(socket_file)

        config = self.set_up_config(yml_file)

        api_data = self.socket_processor.to_json(socket_yml=yml_file, directory=dir_path)
        api_data.update({'instance_name': self.instance.name})
        api_data.update({'config': config})
        custom_socket = CustomSocket.please.create(**api_data)
        self.formatter.write('Sockets {} created.'.format(custom_socket.name))
        self._display_socket_status(custom_socket.name)

    def install_from_url(self, url_path, name):
        socket_yml = self.fetch_file(url_path)
        config = self.set_up_config(socket_yml)
        try:
            CustomSocket(name=name).install_from_url(url=url_path, instance_name=self.instance.name, config=config)
        except SyncanoRequestError as e:
            raise SocketAPIException(e.reason)

        self.formatter.write('Installing Sockets from url: {}.'.format(url_path), SpacedOpt())
        self._display_socket_status(name)

    def _display_socket_status(self, socket_name):
        cs = CustomSocket.please.get(name=socket_name, instance_name=self.instance.name)
        self.formatter.write(
            'Current status is: {} (syncano sockets details {} for refresh).'.format(cs.status, cs.name),
            BottomSpacedOpt())

    def run(self, endpoint_name, method='GET', data=None):
        endpoints = SocketEndpoint.get_all_endpoints(instance_name=self.instance.name)

        for endpoint in endpoints:
            if endpoint.name == endpoint_name:
                run_endpoint = endpoint
                break
        else:
            run_endpoint = None

        if not run_endpoint:
            raise EndpointNotFoundException(format_args=[endpoint_name])
        return run_endpoint.run(method=method, data=data or {})

    def create_template(self, socket_name, destination):

        if not os.path.isdir(destination):
            os.makedirs(destination)

        if not os.path.isdir(os.path.join(destination, 'scripts')):
            os.makedirs(os.path.join(destination, 'scripts'))

        socket = CustomSocket.please.get(name=socket_name, instance_name=self.instance.name)

        yml_file, scripts = self.socket_processor.to_yml(socket_object=socket)

        with open(os.path.join(destination, 'socket.yml'), 'w+') as socket_yml:
            socket_yml.write(yml_file)

        for file_meta in scripts:
            with open(os.path.join(destination, 'scripts/{}'.format(file_meta['file_name'])), 'w+') as script_file:
                script_file.write(file_meta['source'])
        click.echo('INFO: Sockets template created in {}.'.format(destination))

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
        socket_config = SocketConfigParser(socket_yml=socket_yml)
        if socket_config.is_valid():
            return socket_config.ask_for_config()

    def fetch_file(self, url_path):
        response = requests.get(url_path)
        if response.status_code == 200:
            try:
                return yaml.safe_load(response.text)
            except ParserError:
                raise SocketYMLParseException()
        raise SocketFileFetchException(format_args=[url_path])

# -*- coding: utf-8 -*-
import click
from syncano.models import CustomSocket, SocketEndpoint
from syncano_cli.custom_sockets.formatters import SocketFormatter


class SocketParser(object):

    list_line_template = '{socket_name:^29}|{socket_status:^19}|{status_info:^29}'
    socket_line_template = '{endpoint_name:^39}|{calls:^40}'

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
        print('dir publish')

    def publish_from_url(self, ulr_path):
        print('url publish')

    def create_template(self, destination):
        print('template {}'.format(destination))

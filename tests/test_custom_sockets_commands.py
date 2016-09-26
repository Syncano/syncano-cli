# -*- coding: utf-8 -*-
import random
import time

from syncano.models import CustomSocket
from syncano_cli.main import cli
from tests.base import BaseCLITest


class CustomSocketCommandsTest(BaseCLITest):

    @classmethod
    def setUpClass(cls):
        super(CustomSocketCommandsTest, cls).setUpClass()
        cls.suffix = '123{}'.format(random.randint(100, 1000))
        cls.custom_socket = CustomSocket.please.create(
            name='custom_socket_{}'.format(cls.suffix),
            description='custom_description',
            endpoints={
                "custom_endpoint": {
                    "calls": [{"type": "script", "name": "custom_script_{}".format(cls.suffix), "methods": ["*"]}]
                }
            },
            dependencies=[
                {
                    "type": "script",
                    "runtime_name": "python_library_v5.0",
                    "name": "custom_script_{}".format(cls.suffix),
                    "source": "print('script{}', ARGS)".format(cls.suffix)
                }
            ]
        )
        time.sleep(2)  # wait for socket creation;

    def test_dir_install(self):
        socket_base_path = '/tmp/socket_{}'.format('dir_install')
        self.runner.invoke(cli, args=['sockets', 'template', socket_base_path], obj={})

        self.runner.invoke(cli, args=['sockets', 'install', socket_base_path], input='xx-9876\n', obj={})
        time.sleep(2)  # wait for socket creation;

        result = self.runner.invoke(cli, args=['sockets', 'list'], obj={})
        self.assertIn('custom_socket_example', result.output)

        # check config;
        result = self.runner.invoke(cli, args=['sockets', 'config', '{}'.format('custom_socket_example')], obj={})
        self.assertIn('xx-9876', result.output)

    def test_url_install(self):
        path = 'https://raw.githubusercontent.com/Syncano/custom-socket-test/master/socket.yml'
        socket_name = 'my_tweet1'
        self.runner.invoke(cli, args=['sockets', 'install', path, '--name', socket_name],
                           input='testyx\n', obj={})
        time.sleep(2)  # wait for socket creation;

        # check config;
        result = self.runner.invoke(cli, args=['sockets', 'config', '{}'.format(socket_name)], obj={})
        self.assertIn('testyx', result.output)

        result = self.runner.invoke(cli, args=['sockets', 'list'], obj={})
        self.assertIn('my_tweet1', result.output)
        self.assertNotIn('error', result.output)
        # test socket deletion;
        self.runner.invoke(cli, args=['sockets', 'delete', 'my_tweet1'], obj={})
        result = self.runner.invoke(cli, args=['sockets', 'list'], obj={})
        self.assertNotIn('my_tweet1', result.output)

    def test_template_from_socket(self):
        socket_base_path = '/tmp/socket_from_socket'
        self.runner.invoke(cli, args=['sockets', 'template', socket_base_path,
                                      '--socket', self.custom_socket.name], obj={})
        self.assert_file_exists('{}/socket.yml'.format(socket_base_path))
        self.assert_file_exists('{}/scripts/custom_script_{}.py'.format(socket_base_path, self.suffix))

    def test_template_from_local(self):
        socket_base_path = '/tmp/socket{}'.format(self.suffix)
        self.runner.invoke(cli, args=['sockets', 'template', socket_base_path], obj={})
        self.assert_file_exists('{}/socket.yml'.format(socket_base_path))
        self.assert_file_exists('{}/scripts/custom_script.py'.format(socket_base_path))
        self.assert_file_exists('{}/scripts/custom_script_1.py'.format(socket_base_path))
        self.assert_file_exists('{}/scripts/custom_script_2.py'.format(socket_base_path))

    def test_list_sockets(self):
        result = self.runner.invoke(cli, args=['sockets', 'list'], obj={})
        self.assertIn(self.custom_socket.name, result.output)
        self.assertIn('ok', result.output)

    def test_list_endpoints(self):
        result = self.runner.invoke(cli, args=['sockets', 'list', 'endpoints'], obj={})
        self.assertIn('endpoint', result.output)
        self.assertIn('{}/{}'.format(self.custom_socket.name, 'custom_endpoint'), result.output)
        self.assertIn('methods', result.output)

    def test_details_socket(self):
        result = self.runner.invoke(cli, args=['sockets', 'details', self.custom_socket.name], obj={})
        self.assertIn('endpoints', result.output)
        self.assertIn('dependencies', result.output)
        self.assertIn('description', result.output)
        self.assertIn('name', result.output)
        self.assertIn(self.custom_socket.name, result.output)

    def test_run_endpoint(self):
        result = self.runner.invoke(cli, args=['sockets', 'run', '{}/{}'.format(
            self.custom_socket.name,
            'custom_endpoint'
        )], obj={})
        self.assertIn('script{}'.format(self.suffix), result.output)

    def test_run_with_post(self):
        result = self.runner.invoke(cli, args=['sockets', 'run', '{}/{}'.format(
            self.custom_socket.name,
            'custom_endpoint'
        ), 'POST', '-d', 'raz=1'], obj={})
        self.assertIn('script{}'.format(self.suffix), result.output)
        self.assertIn('raz', result.output)

    def test_instance_override(self):
        result = self.runner.invoke(cli, args=['sockets', '--instance-name', 'non-existing-instance-1234',
                                               'run', '{}/{}'.format(self.custom_socket.name,
                                                                     'custom_endpoint')], obj={})
        self.assertIn(u'`non-existing-instance-1234` not found.\n', result.output)

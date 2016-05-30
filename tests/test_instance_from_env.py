import os
import unittest

import mock
from syncano_cli import main  # noqa
from syncano_cli.commands_base import parse_arguments

os.environ.pop('SYNCANO_INSTANCE', None)


class TestException(Exception):
    pass


class TestInstanceFromEnv(unittest.TestCase):

    def test_instance_provided(self):
        os.environ.pop('SYNCANO_INSTANCE', None)
        for cmd in ('pull', 'push'):
            namespace = parse_arguments(['sync', cmd, 'args_instance'])
            self.assertEqual(namespace.instance, 'args_instance')

    def test_instance_not_provided(self):
        os.environ.pop('SYNCANO_INSTANCE', None)
        for cmd in ('pull', 'push'):
            try:
                with mock.patch('sys.stderr'):  # mute errors
                    parse_arguments(['sync', cmd])
            except SystemExit:
                pass
            else:
                raise AssertionError('Instance not provided')

    def test_instance_from_env(self):
        os.environ['SYNCANO_INSTANCE'] = 'environ_instance'
        for cmd in ('pull', 'push'):
            namespace = parse_arguments(['sync', cmd])
            self.assertEqual(namespace.instance, 'environ_instance')
        del os.environ['SYNCANO_INSTANCE']

    def test_instance_from_env_and_provided(self):
        os.environ['SYNCANO_INSTANCE'] = 'environ_instance'
        for cmd in ('pull', 'push'):
            namespace = parse_arguments(['sync', cmd, 'args_instance'])
            self.assertEqual(namespace.instance, 'args_instance')
        del os.environ['SYNCANO_INSTANCE']

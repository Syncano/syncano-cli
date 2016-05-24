import os
import unittest

import mock

os.environ.pop('SYNCANO_INSTANCE', None)


class TestException(Exception):
    pass


class TestInstanceFromEnv(unittest.TestCase):
    def setUp(self):
        from syncano_cli import main
        self.main = main

    def test_instance_provided(self):
        os.environ.pop('SYNCANO_INSTANCE', None)
        for cmd in ('pull', 'push'):
            cmd_mock = mock.Mock(side_effect=TestException(cmd))
            with mock.patch('syncano.connect', cmd_mock):
                try:
                    self.main.cli(['--key', 'api_key', 'sync', cmd, 'args_instance'])
                except TestException:
                    cmd_mock.assert_called_with(
                        api_key='api_key', instance_name='args_instance'
                    )

    def test_instance_not_provided(self):
        os.environ.pop('SYNCANO_INSTANCE', None)
        for cmd in ('pull', 'push'):
            cmd_mock = mock.Mock(side_effect=TestException(cmd))
            with mock.patch('syncano.connect', cmd_mock):
                try:
                    self.main.cli(['--key', 'api_key', 'sync', cmd])
                except SystemExit:
                    pass
                else:
                    raise AssertionError('Instance not provided')

    def test_instance_from_env(self):
        os.environ['SYNCANO_INSTANCE'] = 'environ_instance'
        for cmd in ('pull', 'push'):
            cmd_mock = mock.Mock(side_effect=TestException(cmd))
            with mock.patch('syncano.connect', cmd_mock):
                try:
                    self.main.cli(['--key', 'api_key', 'sync', cmd])
                except TestException:
                    cmd_mock.assert_called_with(
                        api_key='api_key', instance_name='environ_instance'
                    )
        del os.environ['SYNCANO_INSTANCE']

    def test_instance_from_env_and_provided(self):
        os.environ['SYNCANO_INSTANCE'] = 'environ_instance'
        for cmd in ('pull', 'push'):
            cmd_mock = mock.Mock(side_effect=TestException(cmd))
            with mock.patch('syncano.connect', cmd_mock):
                try:
                    self.main.cli(['--key', 'api_key', 'sync', cmd, 'args_instance'])
                except TestException:
                    cmd_mock.assert_called_with(
                        api_key='api_key', instance_name='args_instance'
                    )
        del os.environ['SYNCANO_INSTANCE']

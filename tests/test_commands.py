# -*- coding: utf-8 -*-

import unittest

from click.testing import CliRunner
from syncano_cli.main import cli


class BaseCommandsTest(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.runner = CliRunner()


class SyncCommandsTest(BaseCommandsTest):

    def test_login(self):
        result = self.runner.invoke(cli, args=['login'], obj={})
        self.assertIn('email:', result.output)

    def test_sync_push(self):
        result = self.runner.invoke(cli, args=[
            'sync', 'push', 'test',
            '--class', 'test_class',
            '--scripts', 'test_script',
            '--all',
        ], obj={})
        self.assertIn('', result.output)

    def test_sync_pull(self):
        result = self.runner.invoke(cli, args=[
            'sync', 'pull', 'test',
            '--class', 'test_class',
            '--scripts', 'test_script',
            '--all',
        ], obj={})
        self.assertIn('', result.output)

    def test_watch(self):
        result = self.runner.invoke(cli, args=['sync', 'watch', 'test'], obj={})
        self.assertIn('', result.output)


class TransferCommandsTest(BaseCommandsTest):

    def test_configure(self):
        result = self.runner.invoke(cli, args=['migrate', 'configure'], obj={})
        self.assertIn('PARSE_MASTER_KEY', result.output)

        result = self.runner.invoke(cli, args=['migrate', 'configure', '--force'], obj={})
        self.assertIn('PARSE_MASTER_KEY', result.output)

        result = self.runner.invoke(cli, args=['migrate', 'configure', '--current'], obj={})
        self.assertIn('PARSE_MASTER_KEY', result.output)

    def test_parse(self):
        result = self.runner.invoke(cli, args=['migrate', 'parse'], obj={})
        self.assertIn('Aborted!', result.output)


class ExecuteCommandsTest(BaseCommandsTest):

    def test_execute_execute(self):
        result = self.runner.invoke(cli, args=[
            'execute', 'test_instance', 'test_endpoint',
            '--payload', '{}',
        ], obj={})
        self.assertIn('', result.output)

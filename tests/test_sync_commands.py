# -*- coding: utf-8 -*-
from syncano_cli.main import cli
from tests.base import InstanceMixin, IntegrationTest


class SyncCommandsTest(InstanceMixin, IntegrationTest):

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

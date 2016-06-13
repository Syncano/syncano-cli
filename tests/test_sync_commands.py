# -*- coding: utf-8 -*-
import os

from syncano_cli.config import ACCOUNT_CONFIG, ACCOUNT_CONFIG_PATH
from syncano_cli.main import cli
from tests.base import InstanceMixin, IntegrationTest


class SyncCommandsTest(InstanceMixin, IntegrationTest):

    def test_login(self):
        # tested throught system variables;
        self.runner.invoke(cli, args=['login'], obj={})
        self.assertTrue(ACCOUNT_CONFIG.get('DEFAULT', 'key'))
        self.assertTrue(os.path.isfile(ACCOUNT_CONFIG_PATH))

    def test_sync_push(self):
        result = self.runner.invoke(cli, args=[
            'sync', 'push', 'test',
            '--class', 'test_class',
            '--scripts', 'test_script',
            '--all',
        ], obj={})
        self.assertIn('', result.output)

    def test_sync_pull_class(self):
        self.instance.classes.create(
            name='test_class',
            schema=[
                {'name': 'test_field', 'type': 'string'}
            ]
        )

        self.runner.invoke(cli, args=[
            'sync', 'pull', self.instance.name,
            '--class', 'test_class',
        ], obj={})

        self.assertTrue(os.path.isfile('syncano.yml'))
        with open('syncano.yml') as syncano_yml:
            yml_content = syncano_yml.read()
            self.assertIn('test_class', yml_content)
            self.assertIn('test_field', yml_content)

    def test_sync_all_options(self):
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

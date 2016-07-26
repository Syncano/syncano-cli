# -*- coding: utf-8 -*-
from syncano_cli.main import cli
from tests.base import BaseCLITest


class HostingCommandsTest(BaseCLITest):

    def test_file_list(self):
        self._publish_files()

        result = self.runner.invoke(cli, args=[
            'hosting', self.instance.name, '--list-files'
        ])

        self.assertIn('index.html', result.output)
        self.assertIn('css/page.css', result.output)

    def _publish_files(self):
        result = self.runner.invoke(cli, args=[
            'hosting', self.instance.name, '--publish', 'tests/hosting_files_examples'
        ], obj={})

        self.assertIn('index.html', result.output)
        self.assertIn('css/page.css', result.output)

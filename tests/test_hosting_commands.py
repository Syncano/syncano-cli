# -*- coding: utf-8 -*-

from syncano_cli.main import cli
from tests.base import BaseCLITest


class HostingCommandsTest(BaseCLITest):

    def test_hosting_list(self):

        # create a hosting first:
        domain = 'sunny.day.it'
        self._create_hosting(domain=domain)

        # list available hostings:
        result = self.runner.invoke(cli, args=[
            'hosting', self.instance.name, '--list'
        ])

        self.assertIn('new_label', result.output)
        self.assertIn(domain, result.output)

    def test_file_list(self):
        domain = 'files-list-sunny.day.it'
        self._create_hosting(domain=domain)
        self._publish_files(domain=domain)

        result = self.runner.invoke(cli, args=[
            'hosting', self.instance.name, '--list-files', domain
        ])

        self.assertIn('index.html', result.output)
        self.assertIn('css/page.css', result.output)

    def test_hosting_create(self):
        domain = 'another-sunny.day.it'
        self._create_hosting(domain=domain)

    def test_publish_files(self):
        domain = 'tomorrow-sunny.day.it'
        self._create_hosting(domain=domain)
        self._publish_files(domain)

    def _create_hosting(self, domain):
        result = self.runner.invoke(cli, args=[
            'hosting', self.instance.name, '--create', '--label', 'new_label', domain
        ], obj={})

        self.assertIn('new_label', result.output)
        self.assertIn(domain, result.output)

    def _publish_files(self, domain):
        result = self.runner.invoke(cli, args=[
            'hosting', self.instance.name, '--publish', 'tests/hosting_files_examples', domain
        ], obj={})

        self.assertIn('index.html', result.output)
        self.assertIn('css/page.css', result.output)

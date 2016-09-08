# -*- coding: utf-8 -*-
from syncano_cli.hosting.exceptions import NoDefaultHostingFoundException
from syncano_cli.main import cli
from tests.base import BaseCLITest


class HostingCommandsTest(BaseCLITest):

    def test_hosting_commands(self):
        # test publishing;
        self._publish_files()
        result = self._get_list_output()
        self.assertIn('index.html', result.output)
        self.assertIn('css/page.css', result.output)

        # test single file deletion;
        self._delete_single_file('css/page.css')
        result = self._get_list_output()
        self.assertNotIn('css/page.css', result.output)

        # test update file which do not exist;
        result = self.runner.invoke(cli, args=[
            'hosting', 'update', 'css/page.css', 'tests/hosting_files_examples/css/page.css'
        ], obj={})
        self.assertIn('css/page.css', result.output)

        # test hosting delete;
        self._delete_hosting()
        with self.assertRaises(NoDefaultHostingFoundException):
            self._get_list_output()

        # recreate hosting;
        self._publish_files()

        # test unpublish;
        result = self.runner.invoke(cli, args=[
            'hosting', 'unpublish'
        ], obj={})
        self.assertIn('unpublished', result.output)
        with self.assertRaises(NoDefaultHostingFoundException):
            self._get_list_output()

    def _get_list_output(self):
        result = self.runner.invoke(cli, args=[
            'hosting', 'list'
        ], obj={})
        return result

    def _publish_files(self):
        result = self.runner.invoke(cli, args=[
            'hosting', 'publish', 'tests/hosting_files_examples'
        ], obj={})

        self.assertIn('index.html', result.output)
        self.assertIn('css/page.css', result.output)

    def _delete_single_file(self, path):
        result = self.runner.invoke(cli, args=[
            'hosting', 'delete', path
        ], obj={})

        self.assertIn('deleted.', result.output)

    def _delete_hosting(self):
        result = self.runner.invoke(cli, args=[
            'hosting', 'delete'
        ], input='y', obj={})

        self.assertIn('Hosting', result.output)
        self.assertIn('deleted.', result.output)

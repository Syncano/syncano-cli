# -*- coding: utf-8 -*-
from syncano_cli.main import cli
from tests.base import BaseCLITest


class HostingCommandsTest(BaseCLITest):

    def _base_test(self, domain):
        # test publishing;
        self._publish_files(domain=domain)
        result = self._get_list_files_output(domain=domain)
        self.assertIn('index.html', result.output)
        self.assertIn('css/page.css', result.output)

        # test single file deletion;
        self._delete_single_file('css/page.css', domain=domain)
        result = self._get_list_files_output(domain=domain)
        self.assertNotIn('css/page.css', result.output)

        # test update file which do not exist;
        args = ['hosting', 'update', 'css/page.css', 'tests/hosting_files_examples/css/page.css']
        self._extend_args(args, domain)
        result = self.runner.invoke(cli, args=args, obj={})
        self.assertIn('css/page.css', result.output)

        # test hosting delete;
        self._delete_hosting(domain=domain)
        result = self._get_list_files_output(domain=domain)
        self.assertIn('Hosting with domain `{}` - not found. Exit.'.format(domain or 'default'), result.output)

        # recreate hosting;
        self._publish_files(domain=domain)

    def test_hosting_commands(self):
        self._base_test(domain=None)  # default test

    def test_hosting_with_domains(self):
        self._base_test(domain='efbgh')  # custom domain

    def _get_list_files_output(self, domain=None):
        args = ['hosting', 'list', 'files']
        self._extend_args(args, domain)
        result = self.runner.invoke(cli, args=args, obj={})
        return result

    def _publish_files(self, domain=None):
        args = ['hosting', 'publish', 'tests/hosting_files_examples']
        self._extend_args(args, domain)
        result = self.runner.invoke(cli, args=args, obj={})

        self.assertIn('index.html', result.output)
        self.assertIn('css/page.css', result.output)

    def _delete_single_file(self, path, domain=None):
        args = ['hosting', 'delete', path]
        self._extend_args(args, domain)
        result = self.runner.invoke(cli, args=args, obj={})

        self.assertIn('deleted.', result.output)

    def _delete_hosting(self, domain=None):
        args = ['hosting', 'delete']
        self._extend_args(args, domain)
        result = self.runner.invoke(cli, args=args, input='y', obj={})

        self.assertIn('Hosting', result.output)
        self.assertIn('deleted.', result.output)

    @classmethod
    def _extend_args(cls, args, domain):
        if domain:
            args.insert(1, '--domain')
            args.insert(2, domain)

# -*- coding: utf-8 -*-
from syncano_cli.config import ACCOUNT_CONFIG
from syncano_cli.main import cli
from tests.base import BaseCLITest


class InstancesCommandsTest(BaseCLITest):

    def test_list(self):
        result = self._list_command()
        self.assertIn(self.instance.name, result.output)

    def test_details(self):
        result = self.runner.invoke(cli, args=[
            'instances', 'details', self.instance.name
        ], obj={})
        self.assertIn(self.instance.owner.email, result.output)

    def test_create_and_default_and_delete(self):
        instance_name = 'some-cli-test-instance'
        description = 'some description'
        self.runner.invoke(cli, args=[
            'instances', 'create', instance_name, '--description', description
        ], obj={})

        self.runner.invoke(cli, args=[
            'instances', 'default', instance_name,
        ], obj={})

        self.assert_config_variable_equal(ACCOUNT_CONFIG, 'DEFAULT', 'instance_name', instance_name)

        result = self._list_command()

        self.assertIn(instance_name, result.output)
        self.assertIn(description, result.output)

        self.runner.invoke(cli, args=[
            'instances', 'delete', instance_name,
        ], input='{}\n'.format(instance_name), obj={})

        result = self._list_command()
        self.assertNotIn(instance_name, result.output)
        self.assertNotIn(description, result.output)

    def _list_command(self):
        return self.runner.invoke(cli, args=[
            'instances', 'list'
        ], obj={})

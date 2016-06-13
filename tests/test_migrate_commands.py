# -*- coding: utf-8 -*-
from syncano_cli.main import cli
from tests.base import InstanceMixin, IntegrationTest


class MigrateCommandsTest(InstanceMixin, IntegrationTest):

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

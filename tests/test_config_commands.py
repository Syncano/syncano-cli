# -*- coding: utf-8 -*-
from syncano_cli.main import cli
from tests.base import BaseCLITest


class ConfigCommandsTest(BaseCLITest):

    def test_config(self):
        self._add_config('test', '123')
        result = self._list_config()

        self.assertIn('test', result.output)
        self.assertIn('123', result.output)

    def test_add_config_var(self):
        # test basic add;
        result = self._add_config('api-key', '981xx')
        self.assertIn('Variable `api-key` set to `981xx`.', result.output)

        result = self._list_config()
        self.assertIn('api-key', result.output)
        self.assertIn('981xx', result.output)

        # test if ERROR is displayed;
        result = self._add_config('api-key', '981xx')
        self.assertIn('already in config', result.output)

        # test multiple add;
        self._add_config('totally-new-name', 'new-value')
        result = self._list_config()
        self.assertIn('api-key', result.output)
        self.assertIn('981xx', result.output)
        self.assertIn('totally-new-name', result.output)
        self.assertIn('new-value', result.output)

    def test_modify_config_var(self):
        self._add_config('api-key-mod', '981xx')

        result = self.runner.invoke(cli, args=['config', 'modify', 'api-key-mod', '134'], obj={})
        self.assertIn('Variable `api-key-mod` set to `134`.', result.output)

        result = self._list_config()
        self.assertIn('api-key-mod', result.output)
        self.assertIn('134', result.output)

    def test_delete_config_var(self):
        self._add_config('api-key-del', '981xx')
        result = self._list_config()
        self.assertIn('api-key-del', result.output)

        result = self.runner.invoke(cli, args=['config', 'delete', 'api-key-del'], obj={})
        self.assertIn('Variable `api-key-del` removed.', result.output)

        result = self._list_config()
        self.assertNotIn('api-key-del', result.output)

        # test delete non existing;
        result = self.runner.invoke(cli, args=['config', 'delete', 'api-key-del-non'], obj={})
        self.assertIn('Variable `api-key-del-non` not found.', result.output)

    def _add_config(self, name, value):
        return self.runner.invoke(cli, args=['config', 'add', name, value], obj={})

    def _list_config(self):
        return self.runner.invoke(cli, args=['config'], obj={})

# -*- coding: utf-8 -*-
import os
import random

from syncano_cli.config import DEFAULT_CONFIG_PATH
from syncano_cli.main import cli
from tests.base import BaseCLITest


class AccountCommandsTest(BaseCLITest):

    def test_register(self):
        # remove file with connection data:

        if os.path.isfile(DEFAULT_CONFIG_PATH):
            os.remove(DEFAULT_CONFIG_PATH)
        self.assertFalse(os.path.isfile(DEFAULT_CONFIG_PATH))

        # old api key;
        old_key = self.connection.connection().api_key

        # make register;
        email = 'syncano.bot+977999{}@syncano.com'.format(random.randint(100000, 50000000))
        self.runner.invoke(cli, args=['accounts', 'register', email], input='test1234\ntest1234', obj={})

        # check if api key is written in the config file;
        self.assert_config_variable_exists(self.command.config.global_config, 'DEFAULT', 'key')

        # restore old connection in Syncano LIB; To remove Instance in tearDown;
        self.connection.connection().api_key = old_key

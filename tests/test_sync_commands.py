# -*- coding: utf-8 -*-

from tests.base import InstanceMixin, IntegrationTest


class SyncCommandsTest(InstanceMixin, IntegrationTest):

    def test_self(self):
        self.assertTrue(self.instance.name)

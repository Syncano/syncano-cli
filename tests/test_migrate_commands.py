# -*- coding: utf-8 -*-
import json

import mock
from syncano_cli.config import ACCOUNT_CONFIG
from syncano_cli.main import cli
from syncano_cli.parse_to_syncano.processors.push_notifications import DEVICE_CHANNELS_CLASS_NAME
from tests.base import InstanceMixin, IntegrationTest


class MigrateCommandsTest(InstanceMixin, IntegrationTest):

    @classmethod
    def setUpClass(cls):
        super(MigrateCommandsTest, cls).setUpClass()
        # do a login first;
        cls.runner.invoke(cli, args=['login', '--instance-name', cls.instance.name], obj={})
        # and make setup;
        cls.old_key = cls.connection.connection().api_key
        cls._set_up_configuration()

    @classmethod
    def _set_up_configuration(cls):
        SYNCANO_ADMIN_API_KEY = ACCOUNT_CONFIG.get("DEFAULT", "key")
        if not ACCOUNT_CONFIG.has_section("P2S"):
            ACCOUNT_CONFIG.add_section("P2S")
        ACCOUNT_CONFIG.set("P2S", "PARSE_APPLICATION_ID", "xxx")
        ACCOUNT_CONFIG.set("P2S", "PARSE_MASTER_KEY", "xxx")
        ACCOUNT_CONFIG.set("P2S", "SYNCANO_INSTANCE_NAME", cls.instance.name)
        ACCOUNT_CONFIG.set("P2S", "SYNCANO_ADMIN_API_KEY", SYNCANO_ADMIN_API_KEY)

    def test_configure(self):
        result = self.runner.invoke(cli, args=['migrate', 'configure'], obj={})
        self.assertIn('PARSE_MASTER_KEY', result.output)

        result = self.runner.invoke(cli, args=['migrate', 'configure', '--force'], input='xxx\nxxx\n{}\n{}\n'.format(
            ACCOUNT_CONFIG.get("DEFAULT", "key"),
            self.instance.name,
        ), obj={})
        self.assertIn('PARSE_MASTER_KEY', result.output)

        result = self.runner.invoke(cli, args=['migrate', 'configure', '--current'], obj={})
        self.assertIn('PARSE_MASTER_KEY', result.output)

    def test_parse(self):
        result = self.runner.invoke(cli, args=['migrate', 'parse'], input='N\n', obj={})
        self.assertIn('Transfer aborted.', result.output)

    @mock.patch('syncano_cli.parse_to_syncano.parse.connection.ParseConnection.request')
    @mock.patch('syncano_cli.parse_to_syncano.migrations.transfer.SyncanoTransfer.process_relations',
                mock.MagicMock(return_value=None))
    @mock.patch('syncano_cli.parse_to_syncano.migrations.transfer.SyncanoTransfer.transfer_objects',
                mock.MagicMock(return_value=None))
    @mock.patch('syncano_cli.parse_to_syncano.migrations.transfer.SyncanoTransfer.transfer_files',
                mock.MagicMock(return_value=None))
    def test_class_migrations(self, request_mock):
        with open('tests/json_migrate_mocks/schema.json', 'r+') as f:
            request_mock.return_value = json.loads(f.read())

        self.assertFalse(request_mock.called)
        self.runner.invoke(cli, args=['migrate', 'parse'], obj={}, input='y\n')
        self.assertTrue(request_mock.called)

        syncano_class = self.instance.classes.get(name='test_class_1234')
        self.assertTrue(syncano_class)

        syncano_class = self.instance.classes.get(name='blu_bla')
        self.assertTrue(syncano_class)

    @mock.patch('syncano_cli.parse_to_syncano.parse.connection.ParseConnection.request')
    def test_object_migrations(self, request_mock):
        # create classes first;
        with open('tests/json_migrate_mocks/schema.json', 'r+') as f:
            classes = json.loads(f.read())

        with open('tests/json_migrate_mocks/class_objects.json', 'r+') as f:
            objects = json.loads(f.read())

        with open('tests/json_migrate_mocks/installations.json', 'r+') as f:
            parse_installations = json.loads(f.read())

        # remove blu_bla class from classes;
        classes['results'] = classes['results'][1:]
        # class schemas, objects, break the objects fetch, installations
        request_mock.side_effect = [classes, objects, {'results': []}, parse_installations]

        self.assertFalse(request_mock.called)
        self.runner.invoke(cli, args=['migrate', 'parse'], obj={}, input='y\n')
        self.assertTrue(request_mock.called)

        objects_list = self.instance.classes.get(name='test_class_1234').objects.all()
        self.assertEqual(len([data_object for data_object in objects_list]), 10)

        object_to_test = self.instance.classes.get(name='test_class_1234').objects.filter(
            objectid__eq='ZfowBYpvpw'
        ).first()

        self.assertListEqual(object_to_test.testarray, ["a", "b", "c", "d"])
        self.assertEqual(object_to_test.barg, 12)
        self.assertEqual(object_to_test.carg, True)

        apns_devices = self.instance.apns_devices.all()
        gcm_devices = self.instance.gcm_devices.all()

        self.assertEqual(len([apns_d for apns_d in apns_devices]), 1)
        self.assertEqual(len([gcm_d for gcm_d in gcm_devices]), 1)

        channels_class = self.instance.classes.get(name=DEVICE_CHANNELS_CLASS_NAME)
        self.assertEqual(len([channel_cl for channel_cl in channels_class.objects.all()]), 2)

    @classmethod
    def tearDownClass(cls):
        cls.connection.connection().api_key = cls.old_key
        super(MigrateCommandsTest, cls).tearDownClass()

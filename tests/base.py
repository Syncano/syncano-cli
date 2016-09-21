# -*- coding: utf-8 -*-

import os
import unittest
from datetime import datetime
from hashlib import md5
from uuid import uuid4

import syncano
import yaml
from click.testing import CliRunner
from syncano.models import RuntimeChoices
from syncano_cli.config import ACCOUNT_CONFIG, ACCOUNT_CONFIG_PATH
from syncano_cli.main import cli


class IntegrationTest(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.runner = CliRunner()
        cls.API_KEY = os.getenv('INTEGRATION_API_KEY')
        cls.API_EMAIL = os.getenv('INTEGRATION_API_EMAIL')
        cls.API_PASSWORD = os.getenv('INTEGRATION_API_PASSWORD')
        cls.API_ROOT = os.getenv('INTEGRATION_API_ROOT')

        cls.connection = syncano.connect(
            host=cls.API_ROOT,
            email=cls.API_EMAIL,
            password=cls.API_PASSWORD,
            api_key=cls.API_KEY
        )

    @classmethod
    def tearDownClass(cls):
        cls.connection = None

    @classmethod
    def generate_hash(cls):
        hash_feed = '{}{}'.format(uuid4(), datetime.now())
        return md5(hash_feed.encode('ascii')).hexdigest()


class InstanceMixin(object):

    @classmethod
    def setUpClass(cls):
        super(InstanceMixin, cls).setUpClass()

        cls.instance = cls.connection.Instance.please.create(
            name='test-cli-i%s' % cls.generate_hash()[:10],
            description='IntegrationTest %s' % datetime.now(),
        )

    @classmethod
    def tearDownClass(cls):
        cls.instance.delete()
        super(InstanceMixin, cls).tearDownClass()


class BaseCLITest(InstanceMixin, IntegrationTest):

    @classmethod
    def setUpClass(cls):
        super(BaseCLITest, cls).setUpClass()
        cls.yml_file = 'syncano.yml'
        cls.scripts_dir = 'scripts/'

    def setUp(self):
        self.runner.invoke(cli, args=['login', '--instance-name', self.instance.name], obj={})
        self.assert_config_variable_exists(ACCOUNT_CONFIG, 'DEFAULT', 'key')
        self.assert_config_variable_exists(ACCOUNT_CONFIG, 'DEFAULT', 'instance_name')

    def tearDown(self):
        # remove the .syncano file
        if os.path.isfile(ACCOUNT_CONFIG_PATH):
            os.remove(ACCOUNT_CONFIG_PATH)
        self.assertFalse(os.path.isfile(ACCOUNT_CONFIG_PATH))

    def assert_file_exists(self, path):
        self.assertTrue(os.path.isfile(path))

    def assert_config_variable_exists(self, config, section, key):
        self.assertTrue(config.get(section, key))

    def assert_config_variable_equal(self, config, section, key, value):
        self.assertEqual(config.get(section, key), value)

    def assert_class_yml_file(self, unique):
        with open(self.yml_file) as syncano_yml:
            yml_content = yaml.safe_load(syncano_yml)
            self.assertIn('test_class{unique}'.format(unique=unique), yml_content['classes'])
            self.assertIn('test_field{unique}'.format(unique=unique),
                          yml_content['classes']['test_class{unique}'.format(unique=unique)]['fields'])

    def assert_field_in_schema(self, syncano_class, unique):
        has_field = False
        for field_schema in syncano_class.schema:
            if field_schema['name'] == 'test_field{unique}'.format(unique=unique) and field_schema['type'] == 'string':
                has_field = True
                break

        self.assertTrue(has_field)

    def assert_script_source(self, script_path, assert_source):
        with open(script_path, 'r+') as f:
            source = f.read()
            self.assertEqual(source, assert_source)

    def assert_script_remote(self, script_name, source):
        is_script = False
        check_script = None
        scripts = self.instance.scripts.all()
        for script in scripts:
            if script.label == script_name:
                is_script = True
                check_script = script  # be explicit;
                break
        self.assertTrue(is_script)
        self.assertEqual(check_script.source, source)

    def get_script_path(self, unique):
        return '{dir_name}{script_name}.py'.format(
            dir_name=self.scripts_dir,
            script_name='script_{unique}'.format(unique=unique)
        )

    def modify_yml_file(self, key, object, operation='update'):
        with open(self.yml_file, 'rb') as f:
            yml_syncano = yaml.safe_load(f)
        if operation == 'update':
            yml_syncano[key].update(object)
        elif operation == 'append':
            yml_syncano[key].append(object)
        else:
            raise Exception('not supported operation')

        with open(self.yml_file, 'wt') as f:
            f.write(yaml.safe_dump(yml_syncano, default_flow_style=False))

    def create_syncano_class(self, unique):
        self.instance.classes.create(
            name='test_class{unique}'.format(unique=unique),
            schema=[
                {'name': 'test_field{unique}'.format(unique=unique), 'type': 'string'}
            ]
        )

    def get_class_object_dict(self, unique):
        return {
            'test_class{unique}'.format(unique=unique): {
                'fields': {
                    'test_field{unique}'.format(unique=unique): 'string'
                }
            }
        }

    def get_syncano_class(self, unique):
        return self.instance.classes.get(name='test_class{unique}'.format(unique=unique))

    def create_script(self, unique):
        self.instance.scripts.create(
            runtime_name=RuntimeChoices.PYTHON_V5_0,
            source='print(12)',
            label='script_{unique}'.format(unique=unique)
        )

    def create_script_locally(self, source, unique):
        script_path = 'scripts/script_{unique}.py'.format(unique=unique)
        new_script = {
            'runtime': 'python_library_v5.0',
            'label': 'script_{unique}'.format(unique=unique),
            'script': script_path
        }

        self.modify_yml_file('scripts', new_script, operation='append')

        # create a file also;
        with open(script_path, 'w+') as f:
            f.write(source)

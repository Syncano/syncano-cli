# -*- coding: utf-8 -*-
import os
import unittest

import yaml
from syncano.models import RuntimeChoices
from syncano_cli.config import ACCOUNT_CONFIG, ACCOUNT_CONFIG_PATH
from syncano_cli.main import cli
from tests.base import InstanceMixin, IntegrationTest


class BaseSyncCLITest(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        super(BaseSyncCLITest, cls).setUpClass()
        cls.yml_file = 'syncano.yml'
        cls.scripts_dir = 'scripts/'

    def _assert_file_exists(self, path):
        self.assertTrue(os.path.isfile(path))

    def _assert_config_variable_exists(self, config, section, key):
        self.assertTrue(config.get(section, key))

    def _assert_class_yml_file(self, unique):
        with open(self.yml_file) as syncano_yml:
            yml_content = yaml.safe_load(syncano_yml)
            self.assertIn('test_class{unique}'.format(unique=unique), yml_content['classes'])
            self.assertIn('test_field{unique}'.format(unique=unique),
                          yml_content['classes']['test_class{unique}'.format(unique=unique)]['fields'])

    def _assert_field_in_schema(self, syncano_class, unique):
        has_field = False
        for field_schema in syncano_class.schema:
            if field_schema['name'] == 'test_field{unique}'.format(unique=unique) and field_schema['type'] == 'string':
                has_field = True
                break

        self.assertTrue(has_field)

    def _assert_script_source(self, script_path, assert_source):
        with open(script_path, 'r+') as f:
            source = f.read()
            self.assertEqual(source, assert_source)

    def _assert_script_remote(self, script_name, source):
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

        with open(self.yml_file, 'wb') as f:
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


class SyncCommandsTest(BaseSyncCLITest, InstanceMixin, IntegrationTest):

    def test_login(self):
        # tested through system variables;
        self.runner.invoke(cli, args=['login'], obj={})
        self._assert_config_variable_exists(ACCOUNT_CONFIG, 'DEFAULT', 'key')
        self._assert_file_exists(ACCOUNT_CONFIG_PATH)

    def test_sync_pull_single_class(self):
        unique = '1'
        self.create_syncano_class(unique=unique)

        self.runner.invoke(cli, args=[
            'sync', 'pull', self.instance.name,
            '--class', 'test_class{unique}'.format(unique=unique),
        ], obj={})

        self._assert_file_exists(self.yml_file)
        self._assert_class_yml_file(unique=unique)

    def test_sync_pull_all_classes(self):
        unique = '2'
        self.create_syncano_class(unique=unique)

        self.runner.invoke(cli, args=[
            'sync', 'pull', self.instance.name,
            '--class', 'test_class{unique}'.format(unique=unique),
        ], obj={})

        self._assert_file_exists(self.yml_file)
        self._assert_class_yml_file(unique=unique)

    def test_sync_push_single_class(self):
        # modify yml file first
        unique = '3'
        new_class = self.get_class_object_dict(unique)

        self.modify_yml_file(key='classes', object=new_class)

        # do push
        self.runner.invoke(cli, args=[
            'sync', 'push', self.instance.name,
            '--class', 'test_class{unique}'.format(unique=unique),
        ], obj={})

        # check if class was created;
        new_class_syncano = self.get_syncano_class(unique)
        self.assertTrue(new_class_syncano)

        self._assert_field_in_schema(new_class_syncano, unique)

    def test_sync_push_all_classes(self):
        # modify yml file first
        unique = '4'
        new_class = self.get_class_object_dict(unique)

        self.modify_yml_file(key='classes', object=new_class)

        # do push
        self.runner.invoke(cli, args=[
            'sync', 'push', self.instance.name, '--all'
        ], obj={})

        new_class_syncano = self.get_syncano_class(unique)
        self.assertTrue(new_class_syncano)

    def test_sync_pull_single_script(self):
        unique = 's1'
        self.create_script(unique=unique)

        self.runner.invoke(cli, args=[
            'sync', 'pull', self.instance.name,
            '--script', 'script_{unique}'.format(unique=unique),
        ], obj={})

        script_path = self.get_script_path(unique)
        self._assert_file_exists(script_path)
        self._assert_script_source(script_path, 'print(12)')

    def test_sync_pull_all_scripts(self):
        unique = 's2'
        self.create_script(unique=unique)

        self.runner.invoke(cli, args=[
            'sync', 'pull', self.instance.name, '--all'
        ], obj={})

        script_path = self.get_script_path(unique)
        self._assert_file_exists(script_path)
        self._assert_script_source(script_path, 'print(12)')

    def test_sync_push_single_script(self):
        unique = 's3'
        source = 'print(13)'
        self.create_script_locally(source, unique)

        script_name = 'script_{unique}'.format(unique=unique)
        self.runner.invoke(cli, args=[
            'sync', 'push', self.instance.name,
            '--script', script_name,
        ], obj={})
        self._assert_script_remote(script_name, source)

    def test_sync_push_all_scripts(self):
        unique = 's4'
        source = 'print(14)'
        self.create_script_locally(source, unique)

        script_name = 'script_{unique}'.format(unique=unique)
        self.runner.invoke(cli, args=[
            'sync', 'push', self.instance.name, '--all'
        ], obj={})
        self._assert_script_remote(script_name, source)

    def test_sync_all_options(self):
        result = self.runner.invoke(cli, args=[
            'sync', 'pull', 'test',
            '--class', 'test_class',
            '--scripts', 'test_script',
            '--all',
        ], obj={})
        self.assertIn('', result.output)

    def test_watch(self):
        # Testing this probably is extremely tricky. Leave it.
        result = self.runner.invoke(cli, args=['sync', 'watch', 'test'], obj={})
        self.assertIn('', result.output)

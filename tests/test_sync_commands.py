# -*- coding: utf-8 -*-

from syncano_cli.main import cli
from tests.base import BaseCLITest, InstanceMixin, IntegrationTest


class SyncCommandsTest(BaseCLITest, InstanceMixin, IntegrationTest):

    def test_sync_pull_single_class(self):
        unique = '1'
        self.create_syncano_class(unique=unique)

        self.runner.invoke(cli, args=[
            'sync', 'pull',
            '--class', 'test_class{unique}'.format(unique=unique),
        ], obj={})

        self.assert_file_exists(self.yml_file)
        self.assert_class_yml_file(unique=unique)

    def test_sync_pull_all_classes(self):
        unique = '2'
        self.create_syncano_class(unique=unique)

        self.runner.invoke(cli, args=[
            'sync', 'pull',
            '--class', 'test_class{unique}'.format(unique=unique),
        ], obj={})

        self.assert_file_exists(self.yml_file)
        self.assert_class_yml_file(unique=unique)

    def test_sync_push_single_class(self):
        # modify yml file first
        unique = '3'
        new_class = self.get_class_object_dict(unique)

        self.modify_yml_file(key='classes', object=new_class)

        # do push
        self.runner.invoke(cli, args=[
            'sync', 'push',
            '--class', 'test_class{unique}'.format(unique=unique),
        ], obj={})

        # check if class was created;
        new_class_syncano = self.get_syncano_class(unique)
        self.assertTrue(new_class_syncano)

        self.assert_field_in_schema(new_class_syncano, unique)

    def test_sync_push_all_classes(self):
        # modify yml file first
        unique = '4'
        new_class = self.get_class_object_dict(unique)

        self.modify_yml_file(key='classes', object=new_class)

        # do push
        self.runner.invoke(cli, args=[
            'sync', 'push', '--all'
        ], obj={})

        new_class_syncano = self.get_syncano_class(unique)
        self.assertTrue(new_class_syncano)

    def test_sync_pull_single_script(self):
        unique = 's1'
        self.create_script(unique=unique)

        self.runner.invoke(cli, args=[
            'sync', 'pull',
            '--script', 'script_{unique}'.format(unique=unique),
        ], obj={})

        script_path = self.get_script_path(unique)
        self.assert_file_exists(script_path)
        self.assert_script_source(script_path, 'print(12)')

    def test_sync_pull_all_scripts(self):
        unique = 's2'
        self.create_script(unique=unique)

        self.runner.invoke(cli, args=[
            'sync', 'pull', '--all'
        ], obj={})

        script_path = self.get_script_path(unique)
        self.assert_file_exists(script_path)
        self.assert_script_source(script_path, 'print(12)')

    def test_sync_push_single_script(self):
        unique = 's3'
        source = 'print(13)'
        self.create_script_locally(source, unique)

        script_name = 'script_{unique}'.format(unique=unique)
        self.runner.invoke(cli, args=[
            'sync', 'push',
            '--script', script_name,
        ], obj={})
        self.assert_script_remote(script_name, source)

    def test_sync_push_all_scripts(self):
        unique = 's4'
        source = 'print(14)'
        self.create_script_locally(source, unique)

        script_name = 'script_{unique}'.format(unique=unique)
        self.runner.invoke(cli, args=[
            'sync', 'push', '--all'
        ], obj={})
        self.assert_script_remote(script_name, source)

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

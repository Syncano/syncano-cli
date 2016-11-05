# -*- coding: UTF=8 -*-
import json
import os

import six

if six.PY2:
    from ConfigParser import ConfigParser, NoOptionError, NoSectionError
elif six.PY3:
    from configparser import ConfigParser, NoOptionError, NoSectionError
else:
    raise ImportError()

CONFIGS = ['global', 'local']
DEFAULT_CONFIG_PATH = os.path.join(os.path.expanduser('~'), '.syncano')


class Config(object):
    def __init__(self, global_config_path=None, local_config_path=None):
        self.global_config_path = global_config_path or DEFAULT_CONFIG_PATH
        self.global_config = ConfigParser()
        self.local_config_path = local_config_path
        self.local_config = ConfigParser()

    def read_config(self, config='global'):
        file_path, config_parser = self._get_config_meta(config=config)
        if file_path and os.path.isfile(file_path):
            config_parser.read(file_path)

    def read_configs(self):
        for config in CONFIGS:
            self.read_config(config=config)

    def write_config(self, config='global'):
        file_path, config_parser = self._get_config_meta(config=config)
        if file_path:
            with open(file_path, 'wt') as fp:
                config_parser.write(fp)

    def write_configs(self):
        for config in CONFIGS:
            self.write_config(config=config)

    def add_section(self, section_name, config='global'):
        _, config_parser = self._get_config_meta(config=config)
        if not config_parser.has_section(section_name):
            config_parser.add_section(section_name)

    def has_option(self, section_name, option_name, config='global'):
        _, config_parser = self._get_config_meta(config=config)
        return config_parser.has_option(section_name, option_name)

    def set_config(self, section, option, value, config='global'):
        _, config_parser = self._get_config_meta(config=config)
        config_parser.set(section, option, value)

    def get_config(self, section, option, config='global'):
        _, config_parser = self._get_config_meta(config=config)
        try:
            return config_parser.get(section, option)
        except (NoOptionError, NoSectionError):
            pass

    def _get_config_meta(self, config='global'):
        if config == 'global':
            file_path = self.global_config_path
            config_parser = self.global_config
        elif config == 'local':
            file_path = self.local_config_path
            config_parser = self.local_config
        else:
            raise RuntimeError('available configs: global/local')

        return file_path, config_parser

    def update_info_about_projects(self, project_dir):
        projects = self.get_config('PROJECTS', 'projects')

        if not projects:
            projects = [project_dir]
        else:
            projects = json.loads(projects)
            if project_dir not in projects:
                projects.extend(project_dir)

        if not self.global_config.has_section('PROJECTS'):
            self.global_config.add_section('PROJECTS')

        self.set_config('PROJECTS', 'projects', json.dumps(projects))
        self.write_config()

# coding=UTF8
from __future__ import print_function, unicode_literals

import json
import os
import time

import yaml

from . import LOG
from .classes import pull_classes, push_classes, validate_classes
from .scripts import pull_scripts, push_scripts, validate_scripts


class Project(object):
    def __init__(self, classes=None, scripts=None, timestamp=None, **kwargs):
        self.classes = classes or {}
        self.scripts = scripts or []
        self.timestamp = timestamp or time.time()

    @classmethod
    def from_config(cls, config):
        try:
            with open(config, 'rb') as fp:
                cfg = yaml.safe_load(fp)
            cfg['timestamp'] = os.path.getmtime(config)
        except IOError:
            cfg = {}
        project = cls(**cfg)
        project.validate()
        return project

    def write(self, config):
        with open(config, 'wb') as fp:
            fp.write(yaml.safe_dump({
                'classes': self.classes,
                'scripts': self.scripts
            }, default_flow_style=False))

    def write_json(self, config):
        with open(config, 'wb') as fp:
            json.dump({
                'classes': self.classes,
                'scripts': self.scripts
            }, fp, indent=2)

    def update_from_instance(self, instance, all=False, classes=None,
                             scripts=None):
        """Updates project data from instances"""
        LOG.info("Pulling instance data from syncano")
        classes = classes or self.classes.keys()
        scripts = scripts or set(s['label'] for s in self.scripts)
        if all:
            classes = None
            scripts = None
        self.classes = pull_classes(instance, classes)
        self.scripts = pull_scripts(instance, scripts)
        LOG.info("Finished pulling instance data from syncano")

    def push_to_instance(self, instance, all=False, classes=None,
                         scripts=None):
        try:
            last_sync = os.path.getmtime('.sync')
        except OSError:
            with open('.sync', 'wb'):  # touch file
                pass
            last_sync = 0
        scripts = scripts or self.scripts
        scripts = [s for s in scripts
                   if all or os.path.getmtime(s['script']) > last_sync]

        if scripts:
            push_scripts(instance, scripts)

        sync_classes = self.classes
        if classes and not all:
            sync_classes = {c: self.classes[c] for c in classes}

        if self.timestamp > last_sync:
            push_classes(instance, sync_classes)
        elif not scripts:
            LOG.info('Nothing to sync.')
        now = time.time()
        os.utime('.sync', (now, now))

    def validate(self):
        validate_classes(self.classes)
        validate_scripts(self.scripts)

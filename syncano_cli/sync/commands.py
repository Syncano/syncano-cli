# -*- coding: utf-8 -*-
from __future__ import print_function, unicode_literals

import time

import six
import syncano
from syncano_cli import LOG
from syncano_cli.commands_base import CommandContainer, EnvDefault, argument
from watchdog.observers import Observer

from .watch import ProjectEventHandler

SYNC_NAMESPACE = 'sync'


class Push(six.with_metaclass(CommandContainer)):
    namespace = SYNC_NAMESPACE

    @classmethod
    @argument('-s', '--script', action='append', dest='scripts',
              help="Pull only this script from syncano")
    @argument('-c', '--class', action='append', dest='classes',
              help="Pull only this class from syncano")
    @argument('-a', '--all', action='store_true',
              help="Force push all configuration")
    @argument('instance', help="Destination instance name",
              action=EnvDefault, envvar='SYNCANO_INSTANCE')
    def run(cls, context):
        """
        Push configuration changes to syncano.
        """
        con = syncano.connect(api_key=context.key,
                              instance_name=context.instance)
        context.project.push_to_instance(con, classes=context.classes,
                                         scripts=context.scripts, all=context.all)


class Pull(six.with_metaclass(CommandContainer)):
    namespace = SYNC_NAMESPACE

    @classmethod
    @argument('-s', '--script', action='append', dest='scripts',
              help="Pull only this script from syncano")
    @argument('-c', '--class', action='append', dest='classes',
              help="Pull only this class from syncano")
    @argument('-a', '--all', action='store_true',
              help="Pull all classes/scripts from syncano")
    @argument('instance', help="Source instance name",
              action=EnvDefault, envvar='SYNCANO_INSTANCE')
    def run(cls, context):
        """
        Pull configuration from syncano and store it in current directory.
        Updates syncano.yml configuration file, and places scripts in scripts
        directory.
        When syncano.yml file exists. It will pull only objects defined in
        configuration file. If you want to pull all objects from syncano use
        -a/--all flag.
        """
        con = syncano.connect(api_key=context.key,
                              instance_name=context.instance)
        context.project.update_from_instance(con, context.all,
                                             context.classes, context.scripts)
        context.project.write(context.file)


class Watch(six.with_metaclass(CommandContainer)):
    namespace = SYNC_NAMESPACE

    @classmethod
    @argument('instance', help="Source instance name", action=EnvDefault,
              envvar='SYNCANO_INSTANCE')
    def run(cls, context):
        """
        Push configuration to syncano. After that  watch for changes in
        syncano.yml file and scripts and push changed items to syncano.
        """
        context.classes = None
        context.scripts = None
        context.all = True
        context.project.timestamp = 0
        Push.run(context)
        LOG.info("Watching for file changes")
        observer = Observer()
        observer.schedule(ProjectEventHandler(context), path='.', recursive=True)
        observer.start()
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            observer.stop()
        observer.join()

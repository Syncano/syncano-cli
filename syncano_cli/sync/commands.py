# -*- coding: utf-8 -*-
from __future__ import print_function

import os
import time
from ConfigParser import NoOptionError

import click
import syncano
import sys

from syncano_cli import LOG
from syncano_cli.config import ACCOUNT_CONFIG, ACCOUNT_CONFIG_PATH
from syncano_cli.sync.project import Project
from watchdog.observers import Observer

from .watch import ProjectEventHandler


@click.group()
@click.pass_context
def top_sync(context):
    pass


@top_sync.group()
@click.pass_context
@click.option('-f', '--file', default='syncano.yml', help=u'Instance configuration file.')
@click.option('--config', help=u'Account configuration file.')
@click.option('--key', '--key', default=os.environ.get('SYNCANO_API_KEY', None),
              help=u'override ACCOUNT_KEY used for authentication.')
def sync(context, file, config, key):
    """
    Command for syncing data - classes and scripts
    :param context:
    :param file: file which will be used for syncing
    :param config: the config path - the cli config will be stored there
    :param key: the Syncano API key
    :return:
    """
    config = config or ACCOUNT_CONFIG_PATH
    ACCOUNT_CONFIG.read(config)
    context.obj['file'] = file
    context.obj['config'] = config
    try:
        context.obj['key'] = key or ACCOUNT_CONFIG.get('DEFAULT', 'key')
    except NoOptionError:
        LOG.error('Do a login first: syncano login.')
        sys.exit(1)
    context.obj['project'] = Project.from_config(context.obj['file'])


@sync.command()
@click.pass_context
@click.option('-s', '--script', help=u"Pull only this script from syncano", multiple=True)
@click.option('-c', '--class', help=u"Pull only this class from syncano", multiple=True)
@click.option('-a', '--all', is_flag=True, default=False, help=u"Force push all configuration")
@click.argument('instance', envvar='SYNCANO_INSTANCE')
def push(context, script, all, instance, **kwargs):
    """
    Push configuration changes to syncano.
    """
    klass = kwargs.pop('class')
    do_push(context, scripts=script, classes=klass, all=all, instance=instance)


@sync.command()
@click.pass_context
@click.option('-s', '--script', help=u"Pull only this script from syncano", multiple=True)
@click.option('-c', '--class', help=u"Pull only this class from syncano", multiple=True)
@click.option('-a', '--all', is_flag=True, default=False, help=u"Force push all configuration")
@click.argument('instance', envvar='SYNCANO_INSTANCE')
def pull(context, script, all, instance, **kwargs):
    """
    Pull configuration from syncano and store it in current directory.
    Updates syncano.yml configuration file, and places scripts in scripts
    directory.
    When syncano.yml file exists. It will pull only objects defined in
    configuration file. If you want to pull all objects from syncano use
    -a/--all flag.
    """
    con = syncano.connect(api_key=context.obj['key'], instance_name=instance)
    klass = kwargs.pop('class')
    context.obj['project'].update_from_instance(con, all, klass, script)
    context.obj['project'].write(context.obj['file'])


@sync.command()
@click.pass_context
@click.argument('instance', envvar='SYNCANO_INSTANCE')
def watch(context, instance):
    """
    Push configuration to syncano. After that  watch for changes in
    syncano.yml file and scripts and push changed items to syncano.
    """
    context.obj['classes'] = None
    context.obj['scripts'] = None
    context.obj['all'] = True
    context.obj['project'].timestamp = 0
    context.obj['instance'] = instance
    do_push(context, classes=None, scripts=None, all=True, instance=instance)  # TODO: use context or arguments
    LOG.info(u"Watching for file changes")
    observer = Observer()
    observer.schedule(ProjectEventHandler(context), path='.', recursive=True)
    observer.start()
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()


def do_push(context, classes, scripts, all, instance):
    con = syncano.connect(api_key=context.obj['key'], instance_name=instance)
    context.obj['project'].push_to_instance(con, classes=classes, scripts=scripts, all=all)

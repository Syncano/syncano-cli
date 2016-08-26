# -*- coding: utf-8 -*-
from __future__ import print_function

import os
import sys
import time
from ConfigParser import NoOptionError

import click
import syncano
from syncano_cli.base.connection import get_instance_name
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
@click.option('--key', '--key', default=os.environ.get('SYNCANO_API_KEY'),
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
        click.echo(u'ERROR: Do a login first: syncano login.')
        sys.exit(1)
    context.obj['project'] = Project.from_config(context.obj['file'])


@sync.command()
@click.pass_context
@click.option('-s', '--script', help=u"Pull only this script from syncano", multiple=True)
@click.option('-c', '--class', help=u"Pull only this class from syncano", multiple=True)
@click.option('-a', '--all', is_flag=True, default=False, help=u"Force push all configuration")
@click.option('--instance-name', help=u'Instance name.')
def push(context, script, all, instance_name, **kwargs):
    """
    Push configuration changes to syncano.
    """
    klass = kwargs.pop('class')
    instance_name = get_instance_name(context.obj['config'], instance_name)
    do_push(context, scripts=script, classes=klass, all=all, instance=instance_name)


@sync.command()
@click.pass_context
@click.option('-s', '--script', help=u"Pull only this script from syncano", multiple=True)
@click.option('-c', '--class', help=u"Pull only this class from syncano", multiple=True)
@click.option('-a', '--all', is_flag=True, default=False, help=u"Force push all configuration")
@click.option('--instance-name', help=u'Instance name.')
def pull(context, script, all, instance_name, **kwargs):
    """
    Pull configuration from syncano and store it in current directory.
    Updates syncano.yml configuration file, and places scripts in scripts
    directory.
    When syncano.yml file exists. It will pull only objects defined in
    configuration file. If you want to pull all objects from syncano use
    -a/--all flag.
    """
    instance_name = get_instance_name(context.obj['config'], instance_name)
    con = syncano.connect(api_key=context.obj['key'], instance_name=instance_name)
    klass = kwargs.pop('class')
    context.obj['project'].update_from_instance(con, all, klass, script)
    context.obj['project'].write(context.obj['file'])


@sync.command()
@click.pass_context
@click.option('--instance-name', help=u'Instance name.')
def watch(context, instance_name):
    """
    Push configuration to syncano. After that  watch for changes in
    syncano.yml file and scripts and push changed items to syncano.
    """
    instance_name = get_instance_name(context.obj['config'], instance_name)
    context.obj['classes'] = None
    context.obj['scripts'] = None
    context.obj['all'] = True
    context.obj['project'].timestamp = 0
    context.obj['instance'] = instance_name
    do_push(context, classes=None, scripts=None, all=True, instance=instance_name)  # TODO: use context or arguments
    click.echo(u"INFO: Watching for file changes")
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

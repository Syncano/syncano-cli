# -*- coding: utf-8 -*-
from __future__ import print_function

import os
import time

import click
from click import Abort
from syncano_cli.base.connection import create_connection, get_instance
from syncano_cli.sync.project import Project
from syncano_cli.sync.templates.syncano_yml import syncano_yml
from watchdog.observers import Observer

from .watch import ProjectEventHandler


@click.group()
def top_sync():
    pass


@top_sync.group()
@click.pass_context
@click.option('-f', '--file', default='syncano.yml', help=u'Instance configuration file.')
@click.option('--config', help=u'Account configuration file.')
@click.option('--instance-name', help=u'Instance name.')
def sync(context, file, config, instance_name):
    """
    Sync your scripts and data classes.
    :param context:
    :param file: file which will be used for syncing
    :param config: the config path - the cli config will be stored there
    :return:
    """
    connection = create_connection(config, instance_name)
    context.obj['connection'] = connection
    context.obj['instance'] = get_instance(config, instance_name, connection=connection)
    context.obj['file'] = file
    context.obj['config'] = config
    context.obj['project'] = Project.from_config(context.obj['file'])


@sync.command()
@click.pass_context
@click.option('-s', '--script', help=u"Pull only this script from syncano", multiple=True)
@click.option('-c', '--class', help=u"Pull only this class from syncano", multiple=True)
@click.option('-a', '--all', is_flag=True, default=False, help=u"Force push all configuration")
def push(context, script, all, **kwargs):
    """
    Push configuration changes to syncano.
    """
    klass = kwargs.pop('class')
    print(script, all, klass)
    do_push(context, scripts=script, classes=klass, all=all)


@sync.command()
@click.pass_context
@click.option('-s', '--script', help=u"Pull only this script from syncano", multiple=True)
@click.option('-c', '--class', help=u"Pull only this class from syncano", multiple=True)
@click.option('-a', '--all', is_flag=True, default=False, help=u"Force push all configuration")
def pull(context, script, all, **kwargs):
    """
    Pull configuration from syncano and store it in current directory.
    Updates syncano.yml configuration file, and places scripts in scripts
    directory.
    When syncano.yml file exists. It will pull only objects defined in
    configuration file. If you want to pull all objects from syncano use
    -a/--all flag.
    """
    klass = kwargs.pop('class')
    context.obj['project'].update_from_instance(context.obj['instance'], all, klass, script)
    context.obj['project'].write(context.obj['file'])


@sync.command()
@click.pass_context
def watch(context):
    """
    Push configuration to syncano. After that  watch for changes in
    syncano.yml file and scripts and push changed items to syncano.
    """
    context.obj['classes'] = None
    context.obj['scripts'] = None
    context.obj['all'] = True
    context.obj['project'].timestamp = 0
    do_push(context, classes=None, scripts=None, all=True)  # TODO: use context or arguments
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


@sync.command()
@click.pass_context
def template(context):
    """
    Creates sample project file;
    """
    if os.path.isfile(context.obj['file']):
        confirm = click.confirm(u'Are you sure you want to overwrite syncano.yml file with template?')
        if not confirm:
            raise Abort()

    with open(context.obj['file'], 'wt') as fp:
        fp.write(syncano_yml)
    click.echo("INFO: Template syncano.yml file created.")


def do_push(context, classes, scripts, all):
    scripts = scripts or None
    classes = classes or None
    context.obj['project'].push_to_instance(context.obj['instance'], classes=classes, scripts=scripts, all=all)

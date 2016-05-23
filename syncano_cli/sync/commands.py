# -*- coding: utf-8 -*-
import six
import syncano
from syncano_cli.commands_base import CommandContainer, argument

COMMAND_NAMESPACE = 'sync'


class Push(six.with_metaclass(CommandContainer)):
    namespace = COMMAND_NAMESPACE

    @classmethod
    @argument('-s', '--script', action='append', dest='scripts',
              help="Pull only this script from syncano")
    @argument('-c', '--class', action='append', dest='classes',
              help="Pull only this class from syncano")
    @argument('-a', '--all', action='store_true',
              help="Force push all configuration")
    @argument('instance', help="Destination instance name")
    def run(cls, context):
        """
        Push configuration changes to syncano.
        """
        con = syncano.connect(api_key=context.key)
        instance = con.instances.get(name=context.instance)
        context.project.push_to_instance(instance, classes=context.classes,
                                         scripts=context.scripts, all=context.all)


class Pull(six.with_metaclass(CommandContainer)):
    namespace = COMMAND_NAMESPACE

    @classmethod
    @argument('-s', '--script', action='append', dest='scripts',
              help="Pull only this script from syncano")
    @argument('-c', '--class', action='append', dest='classes',
              help="Pull only this class from syncano")
    @argument('-a', '--all', action='store_true',
              help="Pull all classes/scripts from syncano")
    @argument('instance', help="Source instance name")
    def run(cls, context):
        """
        Pull configuration from syncano and store it in current directory.
        Updates syncano.yml configuration file, and places scripts in scripts
        directory.
        When syncano.yml file exists. It will pull only objects defined in
        configuration file. If you want to pull all objects from syncano use
        -a/--all flag.
        """
        con = syncano.connect(api_key=context.key)
        instance = con.instances.get(name=context.instance)
        context.project.update_from_instance(instance, context.all,
                                             context.classes, context.scripts)
        context.project.write(context.file)

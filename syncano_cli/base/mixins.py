# -*- coding: utf-8 -*-
import sys

import syncano
from syncano.exceptions import SyncanoRequestError
from syncano_cli.base.options import BottomSpacedOpt, ErrorOpt, SpacedOpt, TopSpacedOpt
from syncano_cli.init.helpers import random_instance_name


class RegisterMixin(object):

    def do_login(self, email, password):
        connection = syncano.connect().connection()
        api_key = connection.authenticate(email=email, password=password)
        self.config.set_config('DEFAULT', 'key', api_key)
        self.config.write_config()

    def do_register(self, exc, email, password):
        if exc.status_code == 401:
            if 'email' in exc.message:
                self._register_user(email=email, password=password)
                self.formatter.write('Account created for email: {}'.format(email),
                                     TopSpacedOpt())
            elif 'password' in exc.message:
                self.formatter.write('Invalid login: you have provided wrong password.', ErrorOpt())
                sys.exit(1)

    def create_instance(self):
        instance_name = random_instance_name()
        return self._create_instance(instance_name=instance_name)

    def do_login_or_register(self, email, password):
        try:
            self.do_login(email, password)
        except SyncanoRequestError as exc:
            self.do_register(exc, email, password)

        instances = [i for i in self._list_instances()]
        instance_name = instances[0].name if instances else self.create_instance().name
        self.set_instance_as_default(instance_name)

    def set_instance_as_default(self, instance_name):
        self.formatter.write('Instance `{}` set as default.'.format(instance_name), TopSpacedOpt())
        self._set_instance_as_default(instance_name=instance_name)

    def validate_password(self, password, repeat_password):
        while password != repeat_password:
            self.formatter.write('Password and repeat password are not the same. Please correct:', ErrorOpt(),
                                 SpacedOpt())
            password = self.prompter.prompt('password', hide_input=True)
            repeat_password = self.prompter.prompt('repeat password', hide_input=True)

        return password

    def _register_user(self, email, password, first_name=None, last_name=None):
        connection = syncano.connect().connection()
        api_key = connection.register(
            email=email,
            password=password,
            first_name=first_name,
            last_name=last_name,
        )
        # global context here;
        self.config.set_config('DEFAULT', 'key', api_key)
        self.config.write_config()

    def _create_instance(self, instance_name, description=None, show_default=False):
        kwargs = {
            'name': instance_name
        }
        if description:
            kwargs.update({'description': description})
        instance = self.connection.Instance.please.create(**kwargs)
        self.formatter.write('Instance `{}` created.'.format(instance.name), TopSpacedOpt())
        if show_default:
            self.formatter.write(
                'To set this instance as default use: `syncano instances default {}`'.format(
                    instance.name
                ), BottomSpacedOpt())
        return instance

    def _set_instance_as_default(self, instance_name):
        # global context here;
        self.config.set_config('DEFAULT', 'instance_name', instance_name)
        self.config.write_config()

    def _list_instances(self):
        return self.connection.Instance.please.all()

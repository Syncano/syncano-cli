# -*- coding: utf-8 -*-

from syncano_cli.base.command import BaseCommand


class AccountCommands(BaseCommand):

    def register(self, email, password, first_name=None, last_name=None):
        self._register_user(email, password, first_name=first_name, last_name=last_name)

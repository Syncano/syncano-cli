# -*- coding: utf-8 -*-

import syncano
from syncano.exceptions import SyncanoException
from syncano_cli.base.exceptions import BadCredentialsException, InstanceNotFoundException


class ConnectionMixin(object):

    def get_instance_name(self, instance_name):
        return self.get_config_value(instance_name, 'instance_name')

    def create_connection(self, instance_name=None):
        api_key = self.config.get_config(self.DEFAULT_SECTION, 'key')
        connection_dict = {
            'api_key': api_key,
        }
        instance_name = self.get_instance_name(instance_name)
        if instance_name:
            connection_dict['instance_name'] = instance_name
        try:
            return syncano.connect(**connection_dict)
        except SyncanoException:
            raise BadCredentialsException()

    def get_instance(self, instance_name):
        instance_name = self.get_instance_name(instance_name)
        connection = self.create_connection(instance_name=instance_name)
        try:
            return connection.Instance.please.get(name=instance_name)
        except SyncanoException:
            raise InstanceNotFoundException(format_args=[instance_name])

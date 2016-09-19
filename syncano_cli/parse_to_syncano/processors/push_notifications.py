# -*- coding: utf-8 -*-
import six
from syncano.exceptions import SyncanoException
from syncano.models import Class

DEVICE_CHANNELS_CLASS_NAME = 'internal_device_channels'


class DeviceProcessor(object):

    def __init__(self, data_aggregate):
        self.channel_class = None
        self.data_aggregate = data_aggregate

    def process(self, parse_installation):
        syncano_device = {
            'label': 'Device migrated from parse',
            'registration_id': parse_installation['deviceToken']
        }
        self.handle_channels(parse_installation)
        return syncano_device

    @classmethod
    def find_user(cls, parse_installation):
        for field_name, field_value in six.iteritems(parse_installation):
            if isinstance(field_value, dict) and field_value[u'className'] == u'_User':
                return True, field_value['objectId']
        return False, None

    def handle_channels(self, parse_installation):
        channel_class = self._get_channel_class()
        channels = parse_installation['channels']
        if channels:
            channel_class.objects.create(
                channels=channels,
                registration_id=parse_installation['deviceToken']
            )

    def _get_channel_class(self):
        if self.channel_class is not None:
            return self.channel_class

        schema = [
            {'type': 'array', 'name': 'channels'},
            {'type': 'string', 'name': 'registration_id'},
        ]

        try:
            self.channel_class = Class.please.create(
                name='internal_device_channels',
                schema=schema
            )
        except SyncanoException:
            self.channel_class = Class.please.get(name=DEVICE_CHANNELS_CLASS_NAME)

        return self.channel_class

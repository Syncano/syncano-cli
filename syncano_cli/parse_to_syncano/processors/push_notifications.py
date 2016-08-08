# -*- coding: utf-8 -*-


class DeviceProcessor(object):

    def __init__(self, data_aggregate):
        self.data_aggregate = data_aggregate

    def process(self, parse_installation):
        syncano_device = {}
        is_found, parse_user_id = self.find_user(parse_installation)

        if is_found:
            pass
            # find syncano user_id
            # user_id = self.data_aggregate.reference_map['_User'][parse_user_id]
            # TODO: skip this till the real user creation;
            # syncano_device['user'] = user_id

        syncano_device['registration_id'] = parse_installation['deviceToken']
        return syncano_device

    @classmethod
    def find_user(cls, parse_installation):
        for field_name, field_value in parse_installation.iteritems():
            if isinstance(field_value, dict) and field_value[u'className'] == u'_User':
                return True, field_value['objectId']
        return False, None

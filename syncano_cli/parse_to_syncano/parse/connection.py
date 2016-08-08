# -*- coding: utf-8 -*-
import json

import requests
from syncano_cli.parse_to_syncano.parse.rest_map import PARSE_API_MAP


class ParseConnection(object):

    BASE_URL = 'https://api.parse.com/{url}/'

    def __init__(self, application_id, master_key):
        self.application_id = application_id
        self.master_key = master_key

    def request(self, url, params=None, headers=None):
        params = params or {}
        headers = headers or {}
        url = self.BASE_URL.format(url=url)
        headers.update({
            'X-Parse-Application-Id': self.application_id,
            'X-Parse-Master-Key': self.master_key,
            'Content-Type': 'application/json'
        })
        response = requests.get(url, params=params, headers=headers)
        return response.json()

    def get_schemas(self):
        return self.request(PARSE_API_MAP['schemas'])['results']

    def get_class_objects(self, class_name, limit=1000, skip=0, query=None):
        params = {'limit': limit, 'skip': skip}
        if query:
            params.update({'where': json.dumps(query)})
        return self.request(PARSE_API_MAP['classes'].format(class_name=class_name), params=params)

    def get_installations(self, skip=0, limit=1000):
        params = {'limit': limit, 'skip': skip}
        return self.request(PARSE_API_MAP['installations'], params=params)

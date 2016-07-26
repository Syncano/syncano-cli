# -*- coding: utf-8 -*-

import syncano
from syncano_cli.parse_to_syncano.config import PARSE_PAGINATION_LIMIT
from syncano_cli.parse_to_syncano.parse.connection import ParseConnection


class ParseConnectionMixin(object):

    _parse = None

    @property
    def parse(self):
        if self._parse:
            return self._parse

        parse_connection = ParseConnection(
            application_id=self.config.get('P2S', 'PARSE_APPLICATION_ID'),
            master_key=self.config.get('P2S', 'PARSE_MASTER_KEY'),
        )

        self._parse = parse_connection
        return self._parse


class SyncanoConnectionMixin(object):

    _syncano = None

    @property
    def syncano(self):
        if self._syncano:
            return self._syncano

        syncano_connection = syncano.connect(
            api_key=self.config.get('P2S', 'SYNCANO_ADMIN_API_KEY'),
            instance_name=self.config.get('P2S', 'SYNCANO_INSTANCE_NAME'),
        )

        self._syncano = syncano_connection
        return self._syncano


class PaginationMixin(object):

    @classmethod
    def get_limit_and_skip(cls):
        return PARSE_PAGINATION_LIMIT, 0

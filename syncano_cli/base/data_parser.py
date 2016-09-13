# -*- coding: utf-8 -*-
from syncano_cli.base.exceptions import DataParseException


def parse_input_data(data):
    data_object = {}
    for item in data:
        if '=' not in item:
            raise DataParseException()
        key, value = item.split('=')
        data_object[key.strip()] = value.strip()
    return data_object

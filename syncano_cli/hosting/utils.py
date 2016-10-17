# -*- coding: utf-8 -*-
import re
import unicodedata


def slugify(value):
    value = unicodedata.normalize('NFKD', value).encode('ascii', 'ignore').decode('ascii')
    value = re.sub('[^\w\s-]', '', value).strip().lower()
    value = re.sub('[_]+', '', value)
    return re.sub('[-\s]+', '-', value)

# -*- coding: utf-8 -*-
import os
import re
import unicodedata


def slugify(value):
    value = unicodedata.normalize('NFKD', value).encode('ascii', 'ignore').decode('ascii')
    value = re.sub('[^\w\s-]', '', value).strip().lower()
    value = re.sub('[_]+', '', value)
    return re.sub('[-\s]+', '', value)


class PathFinder(object):

    file_matches = ['index.html']

    def __init__(self, base_dir):
        self.base_dir = base_dir
        self.directories = []
        self._search_for_index_file()

    def __getitem__(self, item):
        return self.directories[item]

    def __len__(self):
        return len(self.directories)

    def _search_for_index_file(self):

        for folder, subs, files in os.walk(self.base_dir):
            for file_name in files:
                if file_name in self.file_matches:
                    self.directories.append(os.path.split(folder)[-1])

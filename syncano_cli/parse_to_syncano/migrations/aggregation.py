# -*- coding: utf-8 -*-

from collections import defaultdict


class ClassAggregate(object):

    def __init__(self, syncano_name, syncano_schema, parse_name, parse_schema):
        self.syncano_name = syncano_name
        self.syncano_schema = syncano_schema
        self.parse_name = parse_name
        self.parse_schema = parse_schema


class DataAggregated(object):

    def __init__(self):
        self.classes = []
        self.reference_map = defaultdict(dict)

    def add_class(self, syncano_name, syncano_schema, parse_name, parse_schema):
        self.classes.append(
            ClassAggregate(syncano_name, syncano_schema, parse_name, parse_schema)
        )

    def sort_classes(self):
        without_relations = []
        with_relations = []
        for _class in self.classes:
            has_relation = False
            for field in _class.syncano_schema:
                if field['type'] == 'reference' or field['type'] == 'relation':
                    has_relation = True
                    break
            if not has_relation:
                without_relations.append(_class)
            else:
                with_relations.append(_class)

        # sort with relations properly; # TODO: some cyclic references

        return without_relations + with_relations


data_aggregate = DataAggregated()

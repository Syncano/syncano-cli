# -*- coding: utf-8 -*-
# a relation helper
from syncano_cli import LOG
from parse_to_syncano.config import PARSE_PAGINATION_LIMIT
from parse_to_syncano.migrations.aggregation import data_aggregate
from parse_to_syncano.migrations.mixins import PaginationMixin, ParseConnectionMixin
from parse_to_syncano.processors.klass import ClassProcessor
from syncano.models import Object


class RelationProcessor(ParseConnectionMixin, PaginationMixin):

    def __init__(self, relations, *args, **kwargs):
        super(RelationProcessor, self).__init__(*args, **kwargs)
        self.relations = relations
        self.reference_map = data_aggregate.reference_map

    def process(self, instance):
        LOG.info('Processing relations...')
        for class_relation in self.relations:
            for class_name, relations in class_relation.iteritems():
                for relation in relations:
                    for field_name, relation_meta in relation.iteritems():
                        target_name = relation_meta['targetClass']

                        # get the parse classes now;
                        for parse_class_name, objects_id_map in self.reference_map.iteritems():
                            if class_name == ClassProcessor.normalize_class_name(parse_class_name):
                                for parse_id, syncano_id in objects_id_map.iteritems():
                                    limit, skip = self.get_limit_and_skip()

                                    while True:

                                        objects = self.get_parse_objects(parse_class_name, parse_id, field_name,
                                                                         target_name, limit, skip)

                                        if not objects['results']:
                                            break

                                        limit += PARSE_PAGINATION_LIMIT
                                        skip += PARSE_PAGINATION_LIMIT

                                        Object.please.update(
                                            **{
                                                field_name: {
                                                    "_add": [
                                                        self.reference_map[target_name][
                                                            data_object['objectId']
                                                        ] for data_object in objects['results']]
                                                },
                                                "class_name": class_name,
                                                "id": syncano_id,
                                                "instance_name": instance.name
                                            }
                                        )

    def get_parse_objects(self, parse_class_name, parse_id, field_name, target_name, limit, skip):
        query = {
            "$relatedTo": {
                "object": {
                    "__type": "Pointer",
                    "className": parse_class_name,
                    "objectId": parse_id},
                "key": field_name}
        }

        return self.parse.get_class_objects(target_name, limit=limit, skip=skip, query=query)

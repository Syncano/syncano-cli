# -*- coding: utf-8 -*-
# a relation helper
import time
from syncano.models import Object
from syncano_cli.logger import get_logger
from syncano_cli.parse_to_syncano.config import PARSE_PAGINATION_LIMIT
from syncano_cli.parse_to_syncano.migrations.aggregation import data_aggregate
from syncano_cli.parse_to_syncano.migrations.mixins import PaginationMixin, ParseConnectionMixin
from syncano_cli.parse_to_syncano.processors.klass import ClassProcessor

LOG = get_logger('parse-to-syncano')


class ClassRelationProcessor(ParseConnectionMixin, PaginationMixin):

    def __init__(self, class_name, relations, config):
        self.class_name = class_name
        self.relations = relations
        self.reference_map = data_aggregate.reference_map
        self.config = config

    def process_class(self, instance):
        for relation in self.relations:
            for field_name, relation_meta in relation.iteritems():
                target_name = relation_meta['targetClass']
                self._find_and_update_relations_objects(
                    field_name=field_name,
                    target_name=target_name,
                    instance=instance
                )

    def _find_and_update_relations_objects(self, field_name, target_name, instance):
        # get the parse classes now;
        for parse_class_name, objects_id_map in self.reference_map.iteritems():
            if self.class_name == ClassProcessor.normalize_class_name(parse_class_name):
                for parse_id, syncano_id in objects_id_map.iteritems():
                    self._find_relations_for_object(
                        parse_class_name=parse_class_name,
                        target_name=target_name,
                        parse_id=parse_id,
                        syncano_id=syncano_id,
                        field_name=field_name,
                        instance=instance
                    )

    def _find_relations_for_object(self, parse_class_name, target_name, parse_id, syncano_id, field_name, instance):
        limit, skip = self.get_limit_and_skip()

        while True:

            objects = self._find_parse_objects(parse_class_name, parse_id, field_name,
                                               target_name, limit, skip)

            if not objects['results']:
                break

            limit += PARSE_PAGINATION_LIMIT
            skip += PARSE_PAGINATION_LIMIT

            self._update_syncano_object(
                field_name=field_name,
                target_name=target_name,
                objects_results=objects['results'],
                syncano_id=syncano_id,
                instance=instance
            )

    def _find_parse_objects(self, parse_class_name, parse_id, field_name, target_name, limit, skip):
        query = {
            "$relatedTo": {
                "object": {
                    "__type": "Pointer",
                    "className": parse_class_name,
                    "objectId": parse_id},
                "key": field_name}
        }

        return self.parse.get_class_objects(target_name, limit=limit, skip=skip, query=query)

    def _update_syncano_object(self, field_name, target_name, objects_results, syncano_id, instance):
        Object.please.update(
            **{
                field_name: {
                    "_add": [
                        self.reference_map[target_name][
                            data_object['objectId']
                        ] for data_object in objects_results]
                },
                "class_name": self.class_name,
                "id": syncano_id,
                "instance_name": instance.name
            }
        )
        time.sleep(1)  # avoid throttling;


class RelationProcessor(object):

    def __init__(self, relations, *args, **kwargs):
        super(RelationProcessor, self).__init__(*args, **kwargs)
        self.relations = relations

    def process(self, instance, config):
        LOG.info('Processing relations...')
        for class_relation in self.relations:
            for class_name, relations in class_relation.iteritems():
                class_relation_processor = ClassRelationProcessor(
                    class_name=class_name,
                    relations=relations,
                    config=config
                )
                class_relation_processor.process_class(instance)

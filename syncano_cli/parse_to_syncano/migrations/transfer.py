# -*- coding: utf-8 -*-
import time

from syncano_cli import LOG
from parse_to_syncano.config import PARSE_PAGINATION_LIMIT, config
from parse_to_syncano.migrations.aggregation import data_aggregate
from parse_to_syncano.migrations.mixins import PaginationMixin, ParseConnectionMixin, SyncanoConnectionMixin
from parse_to_syncano.migrations.relation import RelationProcessor
from parse_to_syncano.processors.klass import ClassProcessor
from syncano.models import Object


class SyncanoTransfer(ParseConnectionMixin, SyncanoConnectionMixin, PaginationMixin):

    def __init__(self):
        super(SyncanoTransfer, self).__init__()
        self.data = data_aggregate
        self.syncano_classes = {}
        self.file_descriptors = {}
        self.relations = None

    def set_relations(self, relations):
        self.relations = relations

    def process_relations(self, instance):
        if self.relations:
            RelationProcessor(relations=self.relations).process(instance=instance)

    def get_syncano_instance(self):
        try:
            instance = self.syncano.Instance.please.get(name=config.get('P2S', 'SYNCANO_INSTANCE_NAME'))
        except:
            instance = self.syncano.Instance.please.create(name=config.get('P2S', 'SYNCANO_INSTANCE_NAME'))

        return instance

    def transfer_classes(self, instance):
        schemas = self.parse.get_schemas()

        relations = []

        for parse_schema in schemas:
            syncano_schema = ClassProcessor.create_schema(parse_schema)
            self.data.add_class(syncano_name=syncano_schema.class_name, syncano_schema=syncano_schema.schema,
                                parse_name=parse_schema['className'], parse_schema=parse_schema)

            if syncano_schema.has_relations:
                relations.append(
                    {
                        syncano_schema.class_name: syncano_schema.relations
                    }
                )

        for class_to_process in self.data.sort_classes():
            try:
                instance.classes.create(name=class_to_process.syncano_name, schema=class_to_process.syncano_schema)
            except Exception as e:
                LOG.warning('Class already defined in this instance: {}/{}; Using existing class'.format(
                    class_to_process.syncano_name, instance.name)
                )
                LOG.warning(e)

        self.set_relations(relations)

    def transfer_objects(self, instance):
        for class_to_process in self.data.sort_classes():
            limit, skip = self.get_limit_and_skip()

            processed = 0
            while True:
                objects = self.parse.get_class_objects(class_to_process.parse_name, limit=limit, skip=skip)
                if not objects['results']:
                    break
                limit += PARSE_PAGINATION_LIMIT
                skip += PARSE_PAGINATION_LIMIT
                objects_to_add = []
                parse_ids = []
                for data_object in objects['results']:
                    s_class = self.get_class(instance=instance, class_name=class_to_process.syncano_name)
                    syncano_object, files = ClassProcessor.process_object(data_object, self.data.reference_map)
                    if files:
                        self.file_descriptors[data_object['objectId']] = (files,
                                                                          class_to_process.syncano_name,
                                                                          class_to_process.parse_name)
                    if len(objects_to_add) == 10:
                        processed += 10
                        created_objects = s_class.objects.batch(
                            *objects_to_add
                        )
                        for parse_id, syncano_id in zip(parse_ids, [o.id for o in created_objects]):
                            self.data.reference_map[class_to_process.parse_name][parse_id] = syncano_id

                        objects_to_add = []
                        parse_ids = []
                        time.sleep(1)  # avoid throttling;
                        LOG.info('Processed {} objects of class {}'.format(processed, class_to_process.syncano_name))

                    batched_syncano_object = s_class.objects.as_batch().create(**syncano_object)
                    objects_to_add.append(batched_syncano_object)
                    parse_ids.append(data_object['objectId'])

                # if objects to add is less than < 10 elements
                if objects_to_add:
                    created_objects = s_class.objects.batch(
                        *objects_to_add
                    )
                    for parse_id, syncano_id in zip(parse_ids, [o.id for o in created_objects]):
                        self.data.reference_map[class_to_process.parse_name][parse_id] = syncano_id
                    LOG.info('Processed {} objects of class: {}'.format(processed + len(objects_to_add),
                                                                        class_to_process.syncano_name))

    def transfer_files(self):
        for parse_id, (files, syncano_class_name, parse_class_name) in self.file_descriptors.iteritems():
            Object.please.update(
                class_name=syncano_class_name,
                id=self.data.reference_map[parse_class_name][parse_id],
                files=files
            )
            time.sleep(4)  # avoid throttling;

    def get_class(self, instance, class_name):
        s_class = self.syncano_classes.get(class_name)
        if not s_class:
            s_class = instance.classes.get(name=class_name)
            self.syncano_classes[class_name] = s_class
        return s_class

    def through_the_red_sea(self):
        instance = self.get_syncano_instance()
        self.transfer_classes(instance)
        self.transfer_objects(instance)
        self.transfer_files()
        self.process_relations(instance)
        LOG.info('Transfer completed')

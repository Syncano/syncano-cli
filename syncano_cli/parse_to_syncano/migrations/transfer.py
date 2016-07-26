# -*- coding: utf-8 -*-
import time

from syncano.models import Object
from syncano_cli.logger import get_logger
from syncano_cli.parse_to_syncano.config import PARSE_PAGINATION_LIMIT
from syncano_cli.parse_to_syncano.migrations.aggregation import data_aggregate
from syncano_cli.parse_to_syncano.migrations.mixins import PaginationMixin, ParseConnectionMixin, SyncanoConnectionMixin
from syncano_cli.parse_to_syncano.migrations.relation import RelationProcessor
from syncano_cli.parse_to_syncano.processors.klass import ClassProcessor

LOG = get_logger('parse-to-syncano')


class SyncanoTransfer(ParseConnectionMixin, SyncanoConnectionMixin, PaginationMixin):

    def __init__(self, config):
        super(SyncanoTransfer, self).__init__()
        self.data = data_aggregate
        self.data.clear()
        self.syncano_classes = {}
        self.file_descriptors = {}
        self.relations = None
        self.config = config

    def set_relations(self, relations):
        self.relations = relations

    def process_relations(self, instance):
        if self.relations:
            RelationProcessor(relations=self.relations).process(instance=instance, config=self.config)

    def get_syncano_instance(self):
        try:
            instance = self.syncano.Instance.please.get(name=self.config.get('P2S', 'SYNCANO_INSTANCE_NAME'))
        except:
            instance = self.syncano.Instance.please.create(name=self.config.get('P2S', 'SYNCANO_INSTANCE_NAME'))

        return instance

    def transfer_classes(self, instance):
        schemas = self.parse.get_schemas()

        relations = []

        for parse_schema in schemas:
            syncano_schema = ClassProcessor.create_schema(parse_schema)
            self.data.add_class(
                syncano_name=syncano_schema.class_name,
                syncano_schema=syncano_schema.schema,
                parse_name=parse_schema['className'],
                parse_schema=parse_schema
            )

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
            time.sleep(1)  # avoid throttling;

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
                objects_to_add, parse_ids = self._clear_data()

                for data_object in objects['results']:
                    s_class = self.get_class(instance=instance, class_name=class_to_process.syncano_name)
                    syncano_object, files = ClassProcessor.process_object(data_object, self.data.reference_map)

                    self._handle_files(files, data_object, class_to_process)

                    if len(objects_to_add) == 10:
                        processed, objects_to_add, parse_ids = self._add_objects(processed, objects_to_add, parse_ids,
                                                                                 s_class, class_to_process)

                    batched_syncano_object = s_class.objects.as_batch().create(**syncano_object)
                    objects_to_add.append(batched_syncano_object)
                    parse_ids.append(data_object['objectId'])

                    time.sleep(6)  # avoid throttling;

                # if objects to add is less than < 10 elements
                if objects_to_add:
                    self._add_last_objects(s_class, objects_to_add, parse_ids, class_to_process, processed)

    def transfer_files(self):
        for parse_id, (files, syncano_class_name, parse_class_name) in self.file_descriptors.iteritems():
            Object.please.update(
                class_name=syncano_class_name,
                id=self.data.reference_map[parse_class_name][parse_id],
                files=files
            )
            time.sleep(1)  # avoid throttling;

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

    def _handle_files(self, files, data_object, class_to_process):
        if files:
            self.file_descriptors[data_object['objectId']] = (
                files,
                class_to_process.syncano_name,
                class_to_process.parse_name
            )

    def _add_last_objects(self, s_class, objects_to_add, parse_ids, class_to_process, processed):
        created_objects = s_class.objects.batch(
            *objects_to_add
        )

        self._update_reference_map(
            class_to_process=class_to_process,
            parse_ids=parse_ids,
            created_objects=created_objects
        )
        self._log_processing(processed + len(objects_to_add), class_to_process.syncano_name)

    def _add_objects(self, processed, objects_to_add, parse_ids, s_class, class_to_process):
        processed += 10
        created_objects = s_class.objects.batch(
            *objects_to_add
        )

        self._update_reference_map(
            class_to_process=class_to_process,
            parse_ids=parse_ids,
            created_objects=created_objects
        )

        objects_to_add, parse_ids = self._clear_data_wait_and_log(processed, class_to_process)

        return processed, objects_to_add, parse_ids

    def _update_reference_map(self, class_to_process, parse_ids, created_objects):
        for parse_id, syncano_id in zip(parse_ids, [o.id for o in created_objects]):
            self.data.reference_map[class_to_process.parse_name][parse_id] = syncano_id

    @classmethod
    def _clear_data(cls):
        return [], []

    @classmethod
    def _clear_data_wait_and_log(cls, processed, class_to_process):
        time.sleep(1)
        cls._log_processing(processed, class_to_process.syncano_name)
        return cls._clear_data()

    @classmethod
    def _log_processing(cls, num, class_name):
        LOG.info('Processed {} objects of class {}'.format(num, class_name))

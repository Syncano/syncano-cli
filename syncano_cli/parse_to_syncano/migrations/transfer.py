# -*- coding: utf-8 -*-
import click
import six
from syncano.exceptions import SyncanoException
from syncano.models import APNSDevice, GCMDevice, Object
from syncano_cli.parse_to_syncano.config import PARSE_PAGINATION_LIMIT, SYNCANO_BATCH_SIZE
from syncano_cli.parse_to_syncano.migrations.aggregation import data_aggregate
from syncano_cli.parse_to_syncano.migrations.mixins import PaginationMixin, ParseConnectionMixin, SyncanoConnectionMixin
from syncano_cli.parse_to_syncano.migrations.relation import RelationProcessor
from syncano_cli.parse_to_syncano.parse.constants import DeviceTypeE
from syncano_cli.parse_to_syncano.processors.klass import ClassProcessor
from syncano_cli.parse_to_syncano.processors.push_notifications import DeviceProcessor


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
            with click.progressbar(
                    self.relations,
                    label='Transferring relations for classes',
                    show_pos=True,
                    item_show_func=ClassProcessor.show_class_name) as classes:
                for class_name, class_relations in classes:
                    RelationProcessor(
                        class_name=class_name,
                        class_relations=class_relations
                    ).process(instance=instance, config=self.config)

    def get_syncano_instance(self):
        try:
            instance = self.syncano.Instance.please.get(name=self.config.get('P2S', 'SYNCANO_INSTANCE_NAME'))
        except SyncanoException:
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
                    (syncano_schema.class_name, syncano_schema.relations)
                )

        sorted_classes = self.data.sort_classes()
        with click.progressbar(
                sorted_classes,
                label='Transferring class schemas',
                show_pos=True,
                item_show_func=ClassProcessor.show_class_name) as classes:
            for class_to_process in classes:
                try:
                    instance.classes.create(name=class_to_process.syncano_name, schema=class_to_process.syncano_schema)
                except Exception as e:
                    click.echo('\nWARN: Class already defined ({}) in this instance ({}). Using existing class.'.format(
                        class_to_process.syncano_name, instance.name)
                    )
                    click.echo('WARN: {}'.format(e))

        self.set_relations(relations)

    def transfer_objects(self, instance):
        sorted_classes = self.data.sort_classes()
        with click.progressbar(
                sorted_classes,
                label='Transferring data objects',
                show_pos=True,
                item_show_func=ClassProcessor.show_class_name) as classes:
            for class_to_process in classes:
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

                        if len(objects_to_add) == SYNCANO_BATCH_SIZE:
                            processed, objects_to_add, parse_ids = self._add_objects(
                                processed, objects_to_add, parse_ids, s_class, class_to_process)

                        batched_syncano_object = s_class.objects.as_batch().create(**syncano_object)
                        objects_to_add.append(batched_syncano_object)
                        parse_ids.append(data_object['objectId'])

                    # if objects to add is less than < 10 elements
                    if objects_to_add:
                        self._add_last_objects(s_class, objects_to_add, parse_ids, class_to_process)

    def transfer_devices(self):
        click.echo(u'Transferring devices')
        limit, skip = self.get_limit_and_skip()
        apns_devices = []
        gcm_devices = []

        device_processor = DeviceProcessor(data_aggregate=self.data)

        while True:
            installations = self.parse.get_installations(limit=limit, skip=skip)
            if not installations['results']:
                break

            for installation in installations['results']:
                syncano_device = device_processor.process(installation)
                if installation['deviceType'] == DeviceTypeE.IOS:
                    apns_devices.append(APNSDevice.please.as_batch().create(**syncano_device))
                elif installation['deviceType'] == DeviceTypeE.ANDROID:
                    gcm_devices.append(GCMDevice.please.as_batch().create(**syncano_device))
                else:
                    click.echo(u'ERROR: Not supported device type: {}. Skipping.'.format(installation['deviceType']))
                    continue

                apns_devices = self._batch_devices(APNSDevice, apns_devices)
                gcm_devices = self._batch_devices(GCMDevice, gcm_devices)

            apns_devices = self._batch_devices(APNSDevice, apns_devices, last=True)
            gcm_devices = self._batch_devices(GCMDevice, gcm_devices, last=True)

            limit += PARSE_PAGINATION_LIMIT
            skip += PARSE_PAGINATION_LIMIT

    def transfer_files(self):
        with click.progressbar(
                self.file_descriptors.keys(),
                label='Transferring files',
                show_pos=True) as parse_ids:
            for parse_id in parse_ids:
                files, syncano_class_name, parse_class_name = self.file_descriptors[parse_id]
                object_to_update = Object(
                    class_name=syncano_class_name,
                    id=self.data.reference_map[parse_class_name][parse_id],
                )

                for file_name, object_file in six.iteritems(files):
                    setattr(object_to_update, file_name, object_file)
                object_to_update.save()

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
        self.transfer_devices()
        self.process_relations(instance)
        click.echo('INFO: Transfer completed')

    def _handle_files(self, files, data_object, class_to_process):
        if files:
            self.file_descriptors[data_object['objectId']] = (
                files,
                class_to_process.syncano_name,
                class_to_process.parse_name
            )

    def _add_last_objects(self, s_class, objects_to_add, parse_ids, class_to_process):
        created_objects = s_class.objects.batch(
            *objects_to_add
        )

        self._update_reference_map(
            class_to_process=class_to_process,
            parse_ids=parse_ids,
            created_objects=created_objects
        )

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

        objects_to_add, parse_ids = self._clear_data_and_wait()

        return processed, objects_to_add, parse_ids

    def _update_reference_map(self, class_to_process, parse_ids, created_objects):
        for parse_id, syncano_id in zip(parse_ids, [o.id for o in created_objects]):
            self.data.reference_map[class_to_process.parse_name][parse_id] = syncano_id

    @classmethod
    def _batch_devices(cls, device_class, devices, last=False):
        if last:
            device_class.please.batch(
                *devices
            )
            return []

        if len(devices) == SYNCANO_BATCH_SIZE:
            device_class.please.batch(
                *devices
            )
            return []

        return devices

    @classmethod
    def _clear_data(cls):
        return [], []

    @classmethod
    def _clear_data_and_wait(cls):
        return cls._clear_data()

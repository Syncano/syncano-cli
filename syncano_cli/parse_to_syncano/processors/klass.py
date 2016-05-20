# -*- coding: utf-8 -*-

import json

import requests
from syncano_cli import LOG
from syncano_cli.parse_to_syncano.parse.constants import ParseFieldTypeE


class SyncanoSchema(object):

    def __init__(self, class_name, schema, relations):
        self.class_name = class_name
        self.schema = schema
        self.relations = relations

    def process_relations(self):
        pass

    @property
    def has_relations(self):
        return bool(self.relations)


class ClassProcessor(object):
    map = {
        'Number': 'integer',
        'Date': 'datetime',
        'Boolean': 'boolean',
        'String': 'string',
        'Array': 'array',
        'Object': 'object',
        'Pointer': 'reference',
        'File': 'file',
        'GeoPoint': 'geopoint',
        'Relation': 'relation',
    }

    @classmethod
    def handle_value(cls, value):
        return value

    @classmethod
    def handle_json_value(cls, value):
        return json.dumps(value)

    @classmethod
    def get_fields(cls, parse_fields):
        FIELDS_TO_SKIP = ['updatedAt', 'createdAt', 'ACL', 'self']  # TODO: handle ACL later on

        fields = []

        for field in parse_fields:
            if field in FIELDS_TO_SKIP:
                continue
            fields.append(field.lower())
        return fields

    @classmethod
    def process_object(cls, parse_object, reference_map):
        syncano_fields = ClassProcessor.get_fields(parse_object.keys())
        processed_object = {}
        files = {}
        for key, value in parse_object.iteritems():
            if isinstance(value, dict):
                if '__type' in value:
                    if value['__type'] == ParseFieldTypeE.RELATION:
                        continue  # will be handled in RelationProcessor
                    cls._process_field_with_type(key, value, processed_object, files, reference_map)
                else:  # and 'Object' case
                    processed_object[key.lower()] = json.dumps(value)
            elif isinstance(value, list):
                cls._process_array_field(key, value, processed_object)

            else:
                cls._process_other_fields(key, value, processed_object, syncano_fields)
        return processed_object, files

    @classmethod
    def _process_field_with_type(cls, key, value, processed_object, files, reference_map):
        if value['__type'] == ParseFieldTypeE.DATE:
            processed_object[key.lower()] = value['iso']
        elif value['__type'] == ParseFieldTypeE.POINTER:
            processed_object[key.lower()] = reference_map.get(value['objectId'])
        elif value['__type'] == ParseFieldTypeE.FILE:
            file_data = requests.get(value['url'])
            file_path = '/tmp/{}'.format(value['name'])
            with open(file_path, 'w+') as file_d:
                file_d.write(file_data.content)
            file_descriptor = open(file_path, 'r')
            files[key] = file_descriptor
        elif value['__type'] == ParseFieldTypeE.GEO_POINT:
            processed_object[key.lower()] = {'longitude': value['longitude'], 'latitude': value['latitude']}

    @classmethod
    def _process_array_field(cls, key, value, processed_object):
        for i, item in enumerate(value):
            if isinstance(item, dict):
                if item.get('__type') == ParseFieldTypeE.POINTER:
                    LOG.warning('Array of pointers not supported, writing: {}'.format(item.get('objectId')))
                    value[i] = item['objectId']
        values_list = json.dumps(value)
        processed_object[key.lower()] = values_list

    @classmethod
    def _process_other_fields(cls, key, value, processed_object, syncano_fields):
        if key.lower() in syncano_fields:
            processed_object[key.lower()] = value

    @classmethod
    def create_schema(cls, parse_schema):
        """
        Return syncano schema for a class;
        :param parse_schema: the schema from parse;
        :return: tha class name and the schema used in Syncano;
        """

        FIELDS_TO_SKIP = ['updatedAt', 'createdAt', 'ACL']  # TODO: handle ACL later on
        class_name = cls.normalize_class_name(parse_schema['className'])
        schema = []
        relations = []
        for field, field_meta in parse_schema['fields'].iteritems():
            if field not in FIELDS_TO_SKIP:
                type = field_meta['type']
                new_type = ClassProcessor.map[type]

                if type == 'Relation':
                    if class_name == cls.normalize_class_name(field_meta['targetClass']):
                        target = 'self'
                    else:
                        target = cls.normalize_class_name(field_meta['targetClass'])
                    schema.append({
                        'name': field.lower(),
                        'type': new_type,
                        'target': target
                    })
                    relations.append({field: field_meta})
                    continue

                if field == 'objectId':
                    schema.append({
                        'name': field.lower(),
                        'type': new_type,
                        'filter_index': True
                    })
                    continue

                if new_type == 'reference':
                    schema.append({
                        'name': field.lower(),
                        'type': new_type,
                        'target': cls.normalize_class_name(field_meta['targetClass'])}
                    )
                    continue

                schema.append({'name': field.lower(), 'type': new_type})

        return SyncanoSchema(class_name=class_name, schema=schema, relations=relations)

    @classmethod
    def normalize_class_name(cls, class_name):
        name = class_name
        if name.startswith('_'):
            name = 'internal_' + name[1:].lower()
        return name

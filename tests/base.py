# -*- coding: utf-8 -*-

import os
import unittest
from datetime import datetime
from hashlib import md5
from uuid import uuid4

import syncano
from click.testing import CliRunner


class BaseCommandsTest(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.runner = CliRunner()


class IntegrationTest(BaseCommandsTest):

    @classmethod
    def setUpClass(cls):
        cls.API_KEY = os.getenv('INTEGRATION_API_KEY')
        cls.API_EMAIL = os.getenv('INTEGRATION_API_EMAIL')
        cls.API_PASSWORD = os.getenv('INTEGRATION_API_PASSWORD')
        cls.API_ROOT = os.getenv('INTEGRATION_API_ROOT')

        cls.connection = syncano.connect(
            host=cls.API_ROOT,
            email=cls.API_EMAIL,
            password=cls.API_PASSWORD,
            api_key=cls.API_KEY
        )

    @classmethod
    def tearDownClass(cls):
        cls.connection = None

    @classmethod
    def generate_hash(cls):
        hash_feed = '{}{}'.format(uuid4(), datetime.now())
        return md5(hash_feed.encode('ascii')).hexdigest()


class InstanceMixin(object):

    @classmethod
    def setUpClass(cls):
        super(InstanceMixin, cls).setUpClass()

        cls.instance = cls.connection.Instance.please.create(
            name='i%s' % cls.generate_hash()[:10],
            description='IntegrationTest %s' % datetime.now(),
        )

    @classmethod
    def tearDownClass(cls):
        cls.instance.delete()
        super(InstanceMixin, cls).tearDownClass()

from datetime import datetime
import unittest

import giraffe.service.db as db
from giraffe.service.db import Host, Meter, MeterRecord


class DbTestCase(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.db = db.connect('mysql://user:pass@127.0.0.1/schema')
        cls.db.session_open()

    @classmethod
    def tearDownClass(cls):
        cls.db.session_close()
        pass

    @classmethod
    def timestamp(self):
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    def setUp(self):
        super(DbTestCase, self).setUp()
        self.meter = Meter(name='unit_test_meter',
                      description='created in setUpClass',
                      unit_name='kb', data_type='int')
        self.db.save(self.meter)
        self.db.commit()

        self.host = Host(name='unti_test_host')
        self.db.save(self.host)
        self.db.commit()

        self.record = MeterRecord(meter_id=self.meter.id,
                                 host_id=self.host.id,
                                 user_id='unit_test_user_id',
                                 resource_id='unit_test_resource_id',
                                 project_id='uni_test_project_id',
                                 value=10,
                                 duration=0,
                                 timestamp=self.timestamp(),
                                 signature='unit_test_signature')
        self.db.save(self.record)
        self.db.commit()

    def tearDown(self):
        super(DbTestCase, self).tearDown()
        self.db.rollback()
        self.db.session_close()

    def test_save_meter_insert(self):
        meter = Meter(name='unit_test_meter',
                      description='created in test_save_meter_insert',
                      unit_name='kb', data_type='int')
        self.db.save(meter)

    def test_load_meter(self):
        meter = self.db.load(Meter, {'id': self.meter.id}, limit=1)[0]
        self.assertEquals(meter.id, self.meter.id)

    def test_save_meter_update(self):
        self.meter.description = 'updated in test_save_meter_update'
        self.db.save(self.meter)
        meter = self.db.load(Meter, {'id': self.meter.id}, limit=1)[0]
        self.assertEqual(self.meter.description, meter.description)

    def test_delete_meter(self):
        self.db.delete(self.record)
        self.db.delete(self.meter)

    def test_save_meter_record_insert(self):
        record = MeterRecord(meter_id=self.meter.id,
                             host_id=self.host.id,
                             user_id='unit_test_user_id',
                             resource_id='unit_test_resource_id',
                             project_id='uni_test_project_id',
                             value=10,
                             duration=0,
                             timestamp=self.timestamp(),
                             signature='unit_test_signature')
        self.db.save(record)

    def test_load_meter_record(self):
        record = self.db.load(MeterRecord, {'id': self.record.id}, limit=1)[0]
        self.assertEquals(record.id, self.record.id)

    def test_save_meter_record_update(self):
        self.record.value = 20
        self.db.save(self.record)
        record = self.db.load(MeterRecord, {'id': self.record.id}, limit=1)[0]
        self.assertEqual(record.value, self.record.value)

    def test_delete_meter_record(self):
        self.db.delete(self.record)

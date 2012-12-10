from datetime import datetime
import unittest

from giraffe.service.db import Connection, Meter, MeterRecord


class DbTestCase(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.db = Connection('mysql://user:pwd@host/schema')
        cls.db.sessionOpen()
        cls.meter = Meter(name='unit_test_meter',
                      description='created in setUpClass',
                      unit_name='kb', data_type='int')
        cls.db.save(cls.meter)
        cls.db.commit()
        cls.record = MeterRecord(meter_id=cls.meter.id,
                                 host_id='unit_test_host_id',
                                 user_id='unit_test_user_id',
                                 resource_id='unit_test_resource_id',
                                 project_id='uni_test_project_id',
                                 message_id='uni_test_msg_id',
                                 value=10,
                                 duration=0,
                                 timestamp=cls.timestamp(),
                                 signature='unit_test_signature')
        cls.db.save(cls.record)
        cls.db.commit()

    @classmethod
    def tearDownClass(cls):
        cls.db.delete(cls.meter)
        cls.db.delete(cls.record)
        cls.db.commit()
        cls.db.sessionClose()

    @classmethod
    def timestamp(self):
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    def setUp(self):
        super(DbTestCase, self).setUp()

    def tearDown(self):
        super(DbTestCase, self).tearDown()
        self.db.rollback()

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
        self.db.delete(self.meter)

    def test_save_meter_record_insert(self):
        record = MeterRecord(meter_id=self.meter.id,
                             host_id='unit_test_host_id',
                             user_id='unit_test_user_id',
                             resource_id='unit_test_resource_id',
                             project_id='uni_test_project_id',
                             message_id='uni_test_msg_id',
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

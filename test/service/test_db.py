import sys

from datetime import datetime
import unittest

import giraffe.service.db as db
from giraffe.service.db import Host, Meter, MeterRecord


class DbTestCases(unittest.TestCase):

    python_version = int(''.join([str(i) for i in sys.version_info[0:3]]))

    @classmethod
    def timestamp(self):
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    @classmethod
    def setUpClass(cls):
        cls.db = db.connect('mysql://user:pwd@27.0.0.1/schema')
        cls.db.session_open()

    @classmethod
    def tearDownClass(cls):
        cls.db.session_close()

    def setUp(self):
        super(DbTestCases, self).setUp()

        if DbTestCases.python_version < 270:
            self.db = db.connect('mysql://user:pwd@27.0.0.1/schema')
            self.db.session_open()

        self.meter = Meter(name='unit_test_meter',
                      description='created in setUp',
                      type='gauge',
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
                                 value='10',
                                 duration=0,
                                 timestamp=self.timestamp(),
                                 signature='unit_test_signature')
        self.db.save(self.record)
        self.db.commit()

    def tearDown(self):
        super(DbTestCases, self).tearDown()
        self.db.rollback()
        self.db.delete(self.record)
        self.db.delete(self.meter)
        self.db.delete(self.host)
        self.db.commit()
        self.db.session_close()

    def test_save_meter_insert(self):
        meter = Meter(name='unit_test_meter',
                      description='created in test_save_meter_insert',
                      unit_name='kb', data_type='int')
        self.db.save(meter)

    def test_load_meter(self):
        meter = self.db.load(Meter, {'id': self.meter.id}, limit=1)[0]
        self.assertEqual(meter.id, self.meter.id)

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
                             value='10',
                             duration=0,
                             timestamp=self.timestamp(),
                             signature='unit_test_signature')
        self.db.save(record)

    def test_load_meter_record(self):
        record = self.db.load(MeterRecord, {'id': self.record.id}, limit=1)[0]
        self.assertEqual(record.id, self.record.id)

    def test_load_meter_record_distinct(self):
        values = self.db.distinct_values(MeterRecord, 'meter_id')
        self.assertEqual(values[-1], self.record.meter_id)

    def test_save_meter_record_update(self):
        self.record.value = '20'
        self.db.save(self.record)
        record = self.db.load(MeterRecord, {'id': self.record.id}, limit=1)[0]
        self.assertEqual(record.value, self.record.value)

    def test_delete_meter_record(self):
        self.db.delete(self.record)

    def test_to_dict(self):
        d = self.record.to_dict()
        self.assertEqual(d['value'], self.record.value)

    #@[fbahr]: IntegrityError: (IntegrityError) (1062, "Duplicate entry '255'
    #          for key 'PRIMARY'") 'INSERT INTO meter (meter_name, meter_desc,
    #          unit_name, data_type, meter_type) VALUES (%s, %s, %s, %s, %s)'
    #          ('unit_test_meter2', 'created in test_load_order', 'kb', 'int',
    #          'gauge')
    def test_load_meter_order(self):
        meter = Meter(name='unit_test_meter2',
                      description='created in test_load_order',
                      type='gauge',
                      unit_name='kb', data_type='int')
        self.db.save(meter)
 
        meters = self.db.load(Meter, order='asc', order_attr='id')
        self.assertTrue(True if len(meters) > 1 else False)
        self.assertEqual(True if meters[0].id < meters[1].id else False, True)

        meters = self.db.load(Meter, order='desc', order_attr='id')
        self.assertTrue(True if len(meters) > 1 else False)
        self.assertEqual(True if meters[0].id > meters[1].id else False, True)

    def test_load_meter_record_order(self):
        record = MeterRecord(meter_id=self.meter.id,
                             host_id=self.host.id,
                             user_id='unit_test_user_id',
                             resource_id='unit_test_resource_id',
                             project_id='uni_test_project_id',
                             value='20',
                             duration=0,
                             timestamp=self.timestamp(),
                             signature='unit_test_signature')
        self.db.save(record)

        records = self.db.load(MeterRecord, order='asc', order_attr='value')
        # built to fail
        self.assertEqual(len(records), 2)
        self.assertEqual(True if records[0].value < records[1].value else False, True)

        records = self.db.load(MeterRecord, order='desc', order_attr='value')
        # built to fail
        self.assertEqual(len(records), 2)
        self.assertEqual(True if records[0].value > records[1].value else False, True)

    def test_count(self):
        meters = self.db.load(Meter)
        meter_count = self.db.count(Meter)
        # host_count = self.db.count(Host, {'name': 'uncinus', 'activity': None})
        host_count = self.db.count(Host, {'name': 'uncinus'})
        self.assertEqual(len(meters), meter_count)
        self.assertEqual(1, host_count)

    #@[fbahr]: crashes in self.db.distinct_values?!
    #          IntegrityError: (IntegrityError) (1062, "Duplicate entry '255'
    #          for key 'PRIMARY'") 'INSERT INTO meter (meter_name, meter_desc,
    #          unit_name, data_type, meter_type) VALUES (%s, %s, %s, %s, %s)'
    #          ('unit_test_dist_meter', 'created in test_distinct', 'bytes',
    #          'int', 'gauge')
    def test_distinct(self):
        meter_name = 'unit_test_dist_meter'
        meter = Meter(name=meter_name,
                      description='created in test_distinct',
                      type='gauge',
                      unit_name='bytes', data_type='int')
        self.db.save(meter)
        distinct_values = self.db.distinct_values(Meter, 'name')
        self.assertTrue(meter_name in distinct_values)

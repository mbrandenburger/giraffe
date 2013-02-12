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
        cls.db = db.connect('mysql://user:pwd@127.0.0.1/schema')
        cls.db.session_open()

    @classmethod
    def tearDownClass(cls):
        cls.db.session_close()

    def setUp(self):
        super(DbTestCases, self).setUp()

        if DbTestCases.python_version < 270:
            self.db = db.connect('mysql://user:pwd@127.0.0.1/schema')
            self.db.session_open()

        timestamp = self.timestamp()
        self.meter = Meter(name='test_' + timestamp,
                      description='created in unit test',
                      type='gauge',
                      unit_name='kb', data_type='int')
        self.db.save(self.meter)
        self.db.commit()

        self.host = Host(name='test_' + timestamp)
        self.db.save(self.host)
        self.db.commit()

        self.record = MeterRecord(meter_id=self.meter.id,
                                 host_id=self.host.id,
                                 user_id='unit_test_user_id',
                                 resource_id='unit_test_resource_id',
                                 project_id='uni_test_project_id',
                                 value='10',
                                 duration=0,
                                 timestamp=self.timestamp())
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
        meter = Meter(name='test_save_meter_insert',
                      description='created in unit test',
                      unit_name='kb', data_type='int')
        self.db.save(meter)

    def test_load_meter(self):
        meter = self.db.load(Meter, {'id': self.meter.id}, limit=1)[0]
        self.assertEqual(meter.id, self.meter.id)

    def test_save_meter_update(self):
        self.meter.description = 'updated in unit test'
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
                             timestamp=self.timestamp())
        self.db.save(record)

    def test_load_meter_record(self):
        record = self.db.load(MeterRecord, {'id': self.record.id}, limit=1)[0]
        self.assertEqual(record.id, self.record.id)

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

    def test_load_order(self):
        meter = Meter(name='test_load_meter_order',
                      description='created in unit test',
                      type='gauge',
                      unit_name='kb', data_type='int')
        self.db.save(meter)

        meters = self.db.load(Meter, order='asc', order_attr='id')
        self.assertTrue(True if len(meters) > 1 else False)
        self.assertEqual(True if meters[0].id < meters[1].id else False, True)

        meters = self.db.load(Meter, order='desc', order_attr='id')
        self.assertTrue(True if len(meters) > 1 else False)
        self.assertEqual(True if meters[0].id > meters[1].id else False, True)

    def test_count(self):
        meters = self.db.load(Meter)
        meter_count = self.db.count(Meter)
        self.assertEqual(len(meters), meter_count)

    def test_distinct(self):
        meter_name = 'test_distinct_' + self.timestamp()
        meter = Meter(name=meter_name,
                      description='created in unit test',
                      type='gauge',
                      unit_name='bytes', data_type='int')
        self.db.save(meter)
        distinct_values = self.db.distinct_values(Meter, 'name')
        self.assertTrue(meter_name in distinct_values)

    def test_sum(self):
        record = MeterRecord(meter_id=self.meter.id,
                             host_id=self.host.id,
                             user_id='unit_test_user_id',
                             resource_id='unit_test_resource_id',
                             project_id='uni_test_project_id',
                             value='100',
                             duration=0,
                             timestamp=self.timestamp())
        self.db.save(record)
        args = {'meter_id': self.meter.id}
        records = self.db.load(MeterRecord, args=args)
        value_sum = 0
        for r in records:
            value_sum += int(r.value)
        self.assertEqual(value_sum, self.db.sum(MeterRecord, 'value',
                                                args=args))

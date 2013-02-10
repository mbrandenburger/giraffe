__author__ = 'fbahr'

import sys
import unittest
import re
from giraffe.common.config import Config
from giraffe.client.api import GiraffeClient
from giraffe.service.db import Host, Meter, MeterRecord


class ClientTestCases(unittest.TestCase):

    python_version = int(''.join([str(i) for i in sys.version_info[0:3]]))

    @classmethod
    def setUpClass(cls):
        cls.gc = GiraffeClient()

    def setUp(self):
        if ClientTestCases.python_version < 270:
            self.gc = GiraffeClient()

    def test_get_set_auth_token(self):
        auth_token = self.gc.auth_token
        self.gc.auth_token = auth_token
        self.assertEqual(auth_token, self.gc.auth_token)

    def test_get_root(self):
        root = self.gc.get_root()
        self.assertIsNotNone(root)
        self.assertTrue(isinstance(root, (str, unicode)))

    def test_get_hosts(self):
        hosts = self.gc.get_hosts()  # tuple (ResultSet) of dicts
        # for h in hosts:
        #     print h
        self.assertTrue(hosts)
        self.assertTrue(isinstance(hosts, (tuple)))

        hosts = hosts._as(Host)  # tuple of Host objects
        self.assertTrue(hosts)
        for h in hosts:
            self.assertTrue(isinstance(h, (Host)))

    def test_get_meters(self):
        meters = self.gc.get_meters()  # tuple (ResultSet) of dicts
        self.assertTrue(meters)
        self.assertTrue(isinstance(meters, (tuple)))

        meters = meters._as(Meter)  # tuple of Meter objects
        self.assertTrue(meters)
        for m in meters:
            self.assertTrue(isinstance(m, (Meter)))

    def test_get_inst_meter_records(self):
        uuid = 'd2b24038-9dee-45d3-876f-d736ddd02d84'

        meter_records = self.gc.get_inst_meter_records( \
                                    inst=uuid,
                                    meter="inst.uptime")
                                    # tuple (ResultSet) of dicts
        self.assertTrue(meter_records)
        self.assertTrue(isinstance(meter_records, (tuple)))

        meter_records = meter_records._as(MeterRecord)
                                    # tuple of MeterRecord objects
        self.assertTrue(meter_records)
        for mr in meter_records:
            self.assertEqual(mr.resource_id, uuid)
            self.assertTrue(isinstance(mr, (MeterRecord)))

    def test_get_host_meter_records(self):
        meter_records = self.gc.get_host_meter_records( \
                                    host='uncinus',
                                    meter="host.loadavg_15m")
                                    # tuple (ResultSet) of dicts
        self.assertTrue(meter_records)
        self.assertTrue(isinstance(meter_records, (tuple)))

        meter_records = meter_records._as(MeterRecord)
                                    # tuple of MeterRecord objects
        self.assertTrue(meter_records)
        for mr in meter_records:
            self.assertTrue(isinstance(mr, (MeterRecord)))

    def test_get_host_meter_records_with_display_limit(self):
        limit = 2
        meter_records = self.gc.get_host_meter_records( \
                                    host='uncinus', \
                                    meter="host.loadavg_15m", \
                                    params={'limit': limit})
        self.assertTrue(len(meter_records) == limit)

    def test_count_host_meter_records(self):
        count = self.gc.get_host_meter_records( \
                            host='uncinus', \
                            meter="host.loadavg_15m", \
                            params={'aggregation': 'count'})
                            # int
        self.assertFalse(isinstance(count, (tuple)))
        self.assertTrue(isinstance(count, (int)))

    def test_count_host_meter_records_with_time_limits(self):
        start_time = '2013-02-07_12-00-00'
        end_time   = '2013-02-07_23-59-59'

        count = self.gc.get_host_meter_records( \
                            host='uncinus', \
                            meter="host.loadavg_15m", \
                            params={'aggregation': 'count'})
                            # int
        self.assertFalse(isinstance(count, (tuple)))
        self.assertTrue(isinstance(count, (int)))

        num_all_records = count

        count = self.gc.get_host_meter_records( \
                            host='uncinus', \
                            meter="host.loadavg_15m", \
                            params={'start_time': start_time, \
                                    'end_time': end_time, \
                                    'aggregation': 'count'})
                                    # int
        self.assertFalse(isinstance(count, (tuple)))
        self.assertTrue(isinstance(count, (int)))

        self.assertLess(count, num_all_records)

    def test_get_min_max_host_meter_record(self):
        _min = self.gc.get_host_meter_records( \
                           host='uncinus', \
                           meter="host.loadavg_15m", \
                           params={'aggregation': 'min'})  # tuple (ResultSet) of dicts
        self.assertTrue(isinstance(_min, (tuple)))
        self.assertTrue(len(_min) == 1)
        _min = _min._as(MeterRecord)[0]  # MeterRecord object
        self.assertTrue(isinstance(_min, (MeterRecord)))

        _max = self.gc.get_host_meter_records( \
                          host='uncinus', \
                          meter="host.loadavg_15m", \
                          params={'aggregation': 'max'})  # tuple (ResultSet) of dicts
        self.assertTrue(isinstance(_max, (tuple)))
        self.assertTrue(len(_max) == 1)
        _max = _max._as(MeterRecord)[0]  # MeterRecord object
        self.assertTrue(isinstance(_max, (MeterRecord)))

        self.assertLessEqual(_min.value, _max.value)

    def test_get_host_meter_records_with_time_limits(self):
        start_time = '2013-02-07_12-00-00'
        end_time   = '2013-02-07_23-59-59'

        regex = re.compile('^(\d{4})-(\d{2})-(\d{2})_(\d{2})-(\d{2})-(\d{2})$')
        matches = regex.match(start_time)
        start_time_repr = '%s-%s-%s %s:%s:%s' % \
                              (matches.group(1), matches.group(2), \
                               matches.group(3), matches.group(4), \
                               matches.group(5), matches.group(6))
        matches = regex.match(end_time)
        end_time_repr = '%s-%s-%s %s:%s:%s' % \
                              (matches.group(1), matches.group(2), \
                               matches.group(3), matches.group(4), \
                               matches.group(5), matches.group(6))

        meter_records = self.gc.get_host_meter_records( \
                                    host='uncinus', \
                                    meter="host.loadavg_15m", \
                                    params={'start_time': start_time, \
                                            'end_time': end_time, \
                                            'order': 'asc'})
                                    # tuple (ResultSet) of dicts
        self.assertTrue(isinstance(meter_records, (tuple)))
        meter_records = meter_records._as(MeterRecord)
        for mr in meter_records:
            self.assertTrue(isinstance(mr, (MeterRecord)))

        start_asc = meter_records[0]
        end_asc = meter_records[-1]
        self.assertLessEqual(start_time_repr, start_asc.timestamp)
        self.assertLessEqual(end_asc.timestamp, end_time_repr)
        self.assertLessEqual(start_asc.timestamp, end_asc.timestamp)

        meter_records = self.gc.get_host_meter_records( \
                                    host='uncinus', \
                                    meter="host.loadavg_15m", \
                                    params={'start_time': start_time, \
                                            'end_time': end_time, \
                                            'order': 'desc'})
                                    # tuple (ResultSet) of dicts
        self.assertTrue(isinstance(meter_records, (tuple)))
        meter_records = meter_records._as(MeterRecord)
        for mr in meter_records:
            self.assertTrue(isinstance(mr, (MeterRecord)))

        start_desc = meter_records[0]
        end_desc = meter_records[-1]
        self.assertEqual(start_asc.timestamp, end_desc.timestamp)
        self.assertTrue(start_desc.timestamp, end_asc.timestamp)
        self.assertTrue(start_desc.timestamp >= end_desc.timestamp)

    def test_get_min_max_host_meter_record_within_time_limits(self):
        start_time = '2013-02-07_20-15-00'
        end_time   = {}
        end_time[0] = '2013-02-07_20-25-59'
        end_time[1] = '2013-02-07_20-40-59'

        abs_min = self.gc.get_host_meter_records( \
                              host='uncinus', \
                              meter="host.loadavg_15m", \
                              params={'aggregation': 'min'}) # tuple (ResultSet) of dicts
        self.assertTrue(len(abs_min) == 1)
        abs_min = abs_min._as(MeterRecord)[0]  # MeterRecord object
        # print abs_min.value, abs_min

        for _, endtime in end_time.iteritems():
            rel_min = self.gc.get_host_meter_records( \
                                  host='uncinus', \
                                  meter="host.loadavg_15m", \
                                  params={'start_time': start_time, \
                                          'end_time': endtime, \
                                          'aggregation': 'min'})  # tuple (ResultSet) of dicts
            if isinstance(rel_min, (tuple)):
                self.assertTrue(len(rel_min) == 1)
                rel_min = rel_min._as(MeterRecord)[0]  # MeterRecord object
                # print rel_min.value, rel_min
                # print abs_min.value, '<=', rel_min.value
                self.assertLessEqual(abs_min.value, rel_min.value)
            else:
                self.assertIsNone(rel_min)

        abs_max = self.gc.get_host_meter_records( \
                              host='uncinus', \
                              meter="host.loadavg_15m", \
                              params={'aggregation': 'max'}) # tuple (ResultSet) of dicts
        self.assertTrue(len(abs_max) == 1)
        abs_max = abs_max._as(MeterRecord)[0]  # MeterRecord object
        # print abs_max.value, abs_max

        for _, endtime in end_time.iteritems():
            rel_max = self.gc.get_host_meter_records( \
                                  host='uncinus', \
                                  meter="host.loadavg_15m", \
                                  params={'start_time': start_time, \
                                          'end_time': endtime, \
                                          'aggregation': 'max'})  # tuple (ResultSet) of dicts
            if isinstance(rel_max, (tuple)):
                self.assertTrue(len(rel_max) == 1)
                rel_max = rel_max._as(MeterRecord)[0]  # MeterRecord object
                # print rel_max.value, rel_max
                # print abs_max.value, '>=', rel_max.value
                self.assertGreaterEqual(abs_max.value, rel_max.value)
            else:
                self.assertIsNone(rel_max)


if __name__ == '__main__':
    unittest.main()

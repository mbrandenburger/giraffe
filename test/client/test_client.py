__author__ = 'fbahr'

import sys
sys.path.insert(0, '/home/fbahr')
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

    def test_get_host_meter_records_with_limit(self):
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

    def test_get_min_max_host_meter_record(self):
        min = self.gc.get_host_meter_records( \
                          host='uncinus', \
                          meter="host.loadavg_15m", \
                          params={'aggregation': 'min'})  # tuple (ResultSet) of dicts
        self.assertTrue(isinstance(min, (tuple)))
        self.assertTrue(len(min) == 1)
        min = min._as(MeterRecord)[0]  # MeterRecord object
        self.assertTrue(isinstance(min, (MeterRecord)))

        max = self.gc.get_host_meter_records( \
                          host='uncinus', \
                          meter="host.loadavg_15m", \
                          params={'aggregation': 'max'})  # tuple (ResultSet) of dicts
        self.assertTrue(isinstance(max, (tuple)))
        self.assertTrue(len(max) == 1)
        max = max._as(MeterRecord)[0]  # MeterRecord object
        self.assertTrue(isinstance(max, (MeterRecord)))

        self.assertTrue(min.value <= max.value)

    def test_get_host_meter_record_time_limits(self):
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
                                    params={'start_time': start_time,
                                            'end_time': end_time,
                                            'order': 'asc'})
                                    # tuple (ResultSet) of dicts
        self.assertTrue(isinstance(meter_records, (tuple)))
        meter_records = meter_records._as(MeterRecord)
        for mr in meter_records:
            self.assertTrue(isinstance(mr, (MeterRecord)))

        start_asc = meter_records[0]
        end_asc = meter_records[-1]
        self.assertTrue(start_time_repr <= start_asc.timestamp)
        self.assertTrue(end_asc.timestamp <= end_time_repr)
        self.assertTrue(start_asc.timestamp <= end_asc.timestamp)

        meter_records = self.gc.get_host_meter_records( \
                                    host='uncinus', \
                                    meter="host.loadavg_15m", \
                                    params={'start_time': start_time,
                                            'end_time': end_time,
                                            'order': 'desc'})
                                    # tuple (ResultSet) of dicts
        self.assertTrue(isinstance(meter_records, (tuple)))
        meter_records = meter_records._as(MeterRecord)
        for mr in meter_records:
            self.assertTrue(isinstance(mr, (MeterRecord)))

        start_desc = meter_records[0]
        end_desc = meter_records[-1]
        self.assertEquals(start_asc.timestamp, end_desc.timestamp)
        self.assertTrue(start_desc.timestamp, end_asc.timestamp)
        self.assertTrue(start_desc.timestamp >= end_desc.timestamp)


if __name__ == '__main__':
    unittest.main()

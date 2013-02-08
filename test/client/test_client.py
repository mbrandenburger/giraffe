__author__ = 'fbahr'

import sys
sys.path.insert(0, '/home/fbahr')
import unittest
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

    def test_min_max_host_meter_record(self):
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


if __name__ == '__main__':
    unittest.main()

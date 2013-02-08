__author__ = 'fbahr'

import sys
import unittest
from giraffe.common.config import Config
from giraffe.client.api import GiraffeClient


class ClientTestCases(unittest.TestCase):

    python_version = int(''.join([str(i) for i in sys.version_info[0:3]]))

    @classmethod
    def setUpClass(cls):
        cls.gc = GiraffeClient()

    def setUp(self):
        if ClientTestCases.python_version < 270:
            self.gc = GiraffeClient()

    def test_get_hosts(self):
        hosts = self.gc.get_hosts()
        # for h in hosts:
        #     print h
        self.assertTrue(hosts)

    def test_get_meters(self):
        meters = self.gc.get_meters()
        self.assertTrue(meters)

#   def test_get_host_meter_records(self):
#       meter_records = self.gc.get_host_meter_records(host='uncinus', meter="loadavg_15m")
#       self.assertTrue(meter_records)

    def test_get_host_meter_records_with_limit(self):
        limit = 2
        meter_records = self.gc.get_host_meter_records( \
                                    host='uncinus', \
                                    meter="host.loadavg_15m", \
                                    params={'limit': limit})
        # for mr in meter_records:
        #     print mr
        self.assertTrue(len(meter_records) == limit)


if __name__ == '__main__':
    unittest.main()

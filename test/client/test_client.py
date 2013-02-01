__author__ = 'fbahr'

import sys
import unittest
from giraffe.common.config import Config
from giraffe.client.client import GiraffeClient


class ClientTestCases(unittest.TestCase):
    """
    For the time being, required a copy of giraffe.cfg to be put in
    giraffe/tests/client
    """

    python_version = int(''.join([str(i) for i in sys.version_info[0:3]]))

    @classmethod
    def setUpClass(cls):
        cls.app = GiraffeClient()

    def setUp(self):
        if ClientTestCases.python_version < 270:
            self.app = GiraffeClient()

    def test_get_hosts(self):
        hosts = self.app.get_hosts()
        self.assertTrue(hosts)

    def test_get_meters(self):
        meters = self.app.get_meters()
        self.assertTrue(meters)

#   def test_get_host_meter_records(self):
#       meter_records = self.app.get_host_meter_records(host='uncinus', meter="loadavg_15m")
#       self.assertTrue(meter_records)

    def test_get_latest_host_meter_record(self):
        latest_meter_record = self.app.get_host_meter_records( \
                                  host='uncinus', \
                                  meter="loadavg_15m", \
                                  params={'latest': 1})
        self.assertTrue(latest_meter_record)


if __name__ == '__main__':
    unittest.main()

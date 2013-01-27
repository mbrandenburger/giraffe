__author__ = 'fbahr'

import sys
import unittest
import logging
from giraffe.agent.inst_meter import Inst_PHYMEM_Usage, Inst_VIRMEM_Usage


class InstMeterTestCases(unittest.TestCase):

    python_version = int(''.join([str(i) for i in sys.version_info[0:3]]))

    logger = logging.getLogger("service.collector.inst_meters")
    logger.setLevel(logging.DEBUG)
    h = logging.StreamHandler()
    h.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
    logger.addHandler(h)


    @classmethod
    def setUpClass(cls):
        if InstMeterTestCases.python_version >= 270:
            cls.inst_phymem_usage = Inst_PHYMEM_Usage(None, 0)
            cls.inst_virmem_usage = Inst_VIRMEM_Usage(None, 0)

    def setUp(self):
        if InstMeterTestCases.python_version < 270:
            self.inst_phymem_usage = Inst_PHYMEM_Usage(None, 0)
            self.inst_virmem_usage = Inst_VIRMEM_Usage(None, 0)

    def test_inst_phymem_usage(self):
        meters = self.inst_phymem_usage.meter()
        self.assertTrue(meters)

    def test_inst_virmem_usage(self):
        meters = self.inst_virmem_usage.meter()
        self.assertTrue(meters)


if __name__ == '__main__':
    unittest.main()

__author__ = 'fbahr'

import sys
import unittest
import logging
from giraffe.agent.instance_meter import Inst_CPU_Time, Inst_PHYMEM_Usage, \
                                         Inst_VIRMEM_Usage, Inst_DISK_IO, \
                                         Inst_NETWORK_IO


class InstMeterTestCases(unittest.TestCase):

    python_version = int(''.join([str(i) for i in sys.version_info[0:3]]))

    logger = logging.getLogger("service.collector.instance_meter")
    logger.setLevel(logging.DEBUG)
    h = logging.StreamHandler()
    h.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
    logger.addHandler(h)

    @classmethod
    def setUpClass(cls):
        cls.inst_cpu = Inst_CPU_Time(None, 0)
        cls.inst_phymem = Inst_PHYMEM_Usage(None, 0)
        cls.inst_virmem = Inst_VIRMEM_Usage(None, 0)
        cls.inst_disk_io = Inst_DISK_IO(None, 0)
        cls.inst_net_io = Inst_NETWORK_IO(None, 0)

    def setUp(self):
        if InstMeterTestCases.python_version < 270:
            self.inst_cpu = Inst_CPU_Time(None, 0)
            self.inst_phymem = Inst_PHYMEM_Usage(None, 0)
            self.inst_virmem = Inst_VIRMEM_Usage(None, 0)
            self.inst_disk_io = Inst_DISK_IO(None, 0)
            self.inst_net_io = Inst_NETWORK_IO(None, 0)

    def test_inst_cpu(self):
        meters = self.inst_cpu.meter()
        # for m in meters:
        #     print m
        self.assertIsNotNone(meters)

    def test_inst_phymem(self):
        meters = self.inst_phymem.meter()
        # for m in meters:
        #     print m
        self.assertIsNotNone(meters)

    def test_inst_virmem(self):
        meters = self.inst_virmem.meter()
        # for m in meters:
        #     print m
        self.assertIsNotNone(meters)

    def test_inst_disk_io(self):
        meters = self.inst_disk_io.meter()
        # for m in meters:
        #     print m
        self.assertIsNotNone(meters)

    def test_inst_net_io(self):
        meters = self.inst_net_io.meter()
        # for m in meters:
        #     print m
        self.assertIsNotNone(meters)


if __name__ == '__main__':
    unittest.main()

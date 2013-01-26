__author__ = 'marcus'

from giraffe.common import Message_pb2

import unittest

class TestSequenceFunctions(unittest.TestCase):
    def setUp(self):
        pass

    def test_shuffle(self):

        hostMsg = Message_pb2.MeterHostMessage()
        hostMsg.hostID = "MacBook"

        record1 = hostMsg.meters.add()
        record1.type = "CPU_AVG"
        record1.value = "1.54"
        record1.duration = 60

        record2 = hostMsg.meters.add()
        record2.type = "CPU_AVG"
        record2.value = "1.84"
        record2.duration = 300

        record3 = hostMsg.meters.add()
        record3.type = "CPU_AVG"
        record3.value = "1.24"
        record3.duration = 1500

        ser_string = hostMsg.SerializeToString()

        eineHostMsg = Message_pb2.MeterHostMessage()
        eineHostMsg.ParseFromString(ser_string)

        self.assertEqual(eineHostMsg.hostID, "MacBook")

        for einRecord in eineHostMsg.meters:
            print einRecord


if __name__ == '__main__':
    unittest.main()
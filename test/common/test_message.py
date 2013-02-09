__author__ = 'marcus, fbahr'

from giraffe.common.message import BulkMessage, HostRecord, InstRecord

import unittest

class TestSequenceFunctions(unittest.TestCase):
    def setUp(self):
        pass

    def test_shuffle(self):

        msg1 = BulkMessage()
        msg1.host_name = "uncinus"

        host_record_1 = msg1.host_records.add()
        host_record_1.meter_name = "CPU_AVG"
        host_record_1.value = "1.54"
        host_record_1.duration = 60
        host_record_1.timestamp = "1"

        host_record_2 = msg1.host_records.add()
        host_record_2.meter_name = "CPU_AVG"
        host_record_2.value = "1.84"
        host_record_2.duration = 300
        host_record_2.timestamp = "2"

        host_record_3 = msg1.host_records.add()
        host_record_3.meter_name = "CPU_AVG"
        host_record_3.value = "1.24"
        host_record_3.duration = 1500
        host_record_3.timestamp = "3"

        ser_string = msg1.SerializeToString()

        try:
            msg2 = BulkMessage()
            msg2.ParseFromString(ser_string)

            self.assertEqual(msg2.host_name, "uncinus")

            for rec in msg2.host_records:
                print rec

        except:
            self.assertEqual(True, False)

        try:
            msg3 = BulkMessage()
            msg3.ParseFromString("muddern")
            self.assertEqual(True, False)
        except:
            self.assertEqual(True, True)


if __name__ == '__main__':
    unittest.main()

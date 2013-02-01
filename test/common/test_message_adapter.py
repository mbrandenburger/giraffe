from datetime import datetime
import unittest

import sys
from giraffe.common.message_adapter import MessageAdapter
from giraffe.common import BulkMessage_pb2


class MessageAdapterTestCases(unittest.TestCase):

    python_version = int(''.join([str(i) for i in sys.version_info[0:3]]))

    @classmethod
    def setUpClass(cls):
        pass

    @classmethod
    def tearDownClass(cls):
        pass

    def setUp(self):
        super(MessageAdapterTestCases, self).setUp()

    def tearDown(self):
        super(MessageAdapterTestCases, self).tearDown()

    def timestamp(self):
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    def serialized_data_str(self):
        adapter = MessageAdapter()
        adapter.signature = 'fake_signature'
        adapter.host_name = 'fake_host_name'
        adapter.add_host_record(timestamp=self.timestamp(),
                                meter_name='fake_meter_name',
                                value='10',
                                duration=0)
        adapter.add_inst_record(project_id='fake_project_id',
                                    user_id='fake_user_id',
                                    inst_id='fake_inst_id',
                                    timestamp=self.timestamp(),
                                    meter_name='fake_meter_name',
                                    value='20',
                                    duration=0)
        return adapter.serialize_to_str()

    def test_init_empty(self):
        adapter = MessageAdapter()
        if MessageAdapterTestCases.python_version < 270:
            self.assertTrue(adapter._adaptee is not None)
        else:
            self.assertIsNotNone(adapter._adaptee)

    def test_init_message(self):
        msg = BulkMessage_pb2.BulkMessage()
        adapter = MessageAdapter(msg)
        self.assertEqual(adapter._adaptee, msg)

    def test_setattr(self):
        adapter = MessageAdapter()
        adapter.signature = 'fake_signature'
        self.assertEqual(adapter._adaptee.signature, 'fake_signature')

    def test_getattr(self):
        adapter = MessageAdapter()
        adapter.host_name = 'fake_host_name'
        self.assertEqual(adapter.host_name, 'fake_host_name')

    def test_add_host_record(self):
        adapter = MessageAdapter()
        self.assertEqual(len(adapter.host_records), 0)
        adapter.add_host_record(timestamp=self.timestamp(),
                                meter_name='fake_meter_name',
                                value='10',
                                duration=0)
        self.assertEqual(len(adapter.host_records), 1)
        self.assertEqual(adapter.host_records[0].value, '10')

    def test_add_inst_record(self):
        adapter = MessageAdapter()
        self.assertEqual(len(adapter.inst_records), 0)
        adapter.add_inst_record(project_id='fake_project_id',
                                    user_id='fake_user_id',
                                    inst_id='fake_inst_id',
                                    timestamp=self.timestamp(),
                                    meter_name='fake_meter_name',
                                    value='20',
                                    duration=0)
        self.assertEqual(len(adapter.inst_records), 1)
        self.assertEqual(adapter.inst_records[0].value, '20')

    def test_serialize_to_str(self):
        adapter = MessageAdapter()
        adapter.signature = 'fake_signature'
        adapter.host_name = 'fake_host_name'
        adapter.add_host_record(timestamp=self.timestamp(),
                                meter_name='fake_meter_name',
                                value='10',
                                duration=0)
        adapter.add_inst_record(project_id='fake_project_id',
                                    user_id='fake_user_id',
                                    inst_id='fake_inst_id',
                                    timestamp=self.timestamp(),
                                    meter_name='fake_meter_name',
                                    value='20',
                                    duration=0)
        self.assertEqual(isinstance(adapter.serialize_to_str(), str), True)

    def test_deserialize_to_str(self):
        adapter = MessageAdapter()
        adapter.deserialize_from_str(self.serialized_data_str())
        self.assertEqual(adapter.signature, 'fake_signature')
        self.assertEqual(adapter.host_name, 'fake_host_name')
        self.assertEqual(adapter.host_records[0].value, '10')
        self.assertEqual(adapter.inst_records[0].value, '20')

    def test_deserialize_to_str_constructor(self):
        adapter = MessageAdapter(self.serialized_data_str())
        self.assertEqual(adapter.signature, 'fake_signature')
        self.assertEqual(adapter.host_name, 'fake_host_name')
        self.assertEqual(adapter.host_records[0].value, '10')
        self.assertEqual(adapter.inst_records[0].value, '20')

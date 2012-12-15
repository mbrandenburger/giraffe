from datetime import datetime
import unittest

from giraffe.common.message_adapter import MessageAdapter
from giraffe.common import BulkMessage_pb2


class MessageAdapterTestCase(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        pass

    @classmethod
    def tearDownClass(cls):
        pass

    def setUp(self):
        super(MessageAdapterTestCase, self).setUp()

    def tearDown(self):
        super(MessageAdapterTestCase, self).tearDown()

    def timestamp(self):
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    def test_init_empty(self):
        adapter = MessageAdapter()
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
        adapter.host_id = 'fake_host_id'
        self.assertEqual(adapter.host_id, 'fake_host_id')

    def test_add_host_record(self):
        adapter = MessageAdapter()
        self.assertEqual(len(adapter.host_records), 0)
        adapter.add_host_record(timestamp=self.timestamp(),
                                meter_type='fake_meter_type',
                                value='10',
                                duration=0)
        self.assertEqual(len(adapter.host_records), 1)
        self.assertEqual(adapter.host_records[0].value, '10')

    def test_add_instance_record(self):
        adapter = MessageAdapter()
        self.assertEqual(len(adapter.instance_records), 0)
        adapter.add_instance_record(project_id='fake_project_id',
                                    user_id='fake_user_id',
                                    instance_id='fake_instance_id',
                                    timestamp=self.timestamp(),
                                    meter_type='fake_meter_type',
                                    value='20',
                                    duration=0)
        self.assertEqual(len(adapter.instance_records), 1)
        self.assertEqual(adapter.instance_records[0].value, '20')

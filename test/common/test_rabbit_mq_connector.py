__author__ = 'marcus'

import unittest
from giraffe.common.rabbit_mq_connector import *


# global constants
testMessagesCount = 10
testMessagesReceived = 0
timeout_sec = 5


def _consumer_call(ch, body):
    global testMessagesCount
    global testMessagesReceived

    testMessagesReceived += 1
    print "Got one %i" % testMessagesReceived

    if testMessagesReceived >= testMessagesCount:
        ch.stop_consuming()


class TestSequenceFunctions(unittest.TestCase):
    def setUp(self):
        self.connector = Connector(host='cloud2.ibr.cs.tu-bs.de')
        self.connector.connect()
        self.queue = "my_testQ"
        self.exchange = "my_testEX"
        self.routing_key = ''
        self.testMessage = 'Fun with icecream'

    def tearDown(self):
        self.connector.close()

    def test_produce(self):
        self.producer = BasicProducer(self.connector, self.exchange)
        for i in range(0, testMessagesCount, 1):
            print "Send %i" % i
            self.producer.send(self.exchange, self.routing_key,
                               self.testMessage)

    def test_consume(self):
        self.consumer = BasicConsumer(self.connector, self.queue,
                                      self.exchange, _consumer_call)
        self.consumer.consume()
        self.assertEqual(testMessagesCount, testMessagesReceived)


if __name__ == '__main__':
    unittest.main()

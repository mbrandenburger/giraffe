__author__ = 'marcus'

from giraffe.common.rabbit_mq_connector import *
from time import sleep
import unittest

testMessagesCount = 10
testMessagesReceived = 0
timeout_sec = 5

def _consumer_call(ch, method, properties, body):
    global testMessagesCount
    global testMessagesReceived

    testMessagesReceived += 1
#    print "Got one %i" % testMessagesReceived

    if testMessagesReceived >= testMessagesCount:
        ch.stop_consuming()

class TestSequenceFunctions(unittest.TestCase):
    def setUp(self):

        self.connector = Connector('cloud2.ibr.cs.tu-bs.de')
        self.queue = "giraffe_test"
        self.exchange = "giraffe_topic"
        self.routing_key = ''
        self.testMessage = 'Fun with icecream'

    def test_produce(self):
        self.producer = BasicProducer(self.connector, self.exchange)
        for i in range(0,testMessagesCount,1):
            self.producer.send(self.exchange, self.routing_key, self.testMessage)

    def test_Consume(self):
        self.consumer = BasicConsumer(self.connector, self.queue, self.exchange, _consumer_call)
        self.consumer.consume()
        self.assertEqual(testMessagesCount, testMessagesReceived)


if __name__ == '__main__':
    unittest.main()
__author__ = 'marcus'

from giraffe.common.rabbit_mq_connector import *

class AgentPublisher(object):

    def __init__(self):
        self.connector = Connector('cloud2.ibr.cs.tu-bs.de')
        self.queue = "giraffe_test"
        self.exchange = "giraffe_topic"
        self.routing_key = ''

    def publish(self,params):
        self.producer = BasicProducer(self.connector, self.queue, self.exchange)
        self.producer.send(self.exchange, self.routing_key, params)
from giraffe.common.RabbitMQConnector import Connector, BasicConsumer
from test import daemon

__author__ = 'mbrandenburger'

import MySQLdb as db

class CoreService(object):

    def __init__(self):
        self.connector = Connector('cloud2.ibr.cs.tu-bs.de')
        self.queue = "giraffe_test"
        self.exchange = "giraffe_topic"
        self.routing_key = ''
        self.dbconnection = db.connect('cloud2.ibr.cs.tu-bs.de', 'giraffedbadmin',
                                       'aff3nZo0', 'giraffe')
    
    def start(self):
        self.consumer = BasicConsumer(self.connector, self.queue, self.exchange, self._consumer_call)
        self.consumer.consume()
    
    def _consumer_call(self, ch, method, properties, body):
        print " -> %r:%r" % (method,body,)
        with self.dbconnection:
            cur = self.dbconnection.cursor()
            cur.execute("INSERT INTO compute_log(logging_message) VALUES(%s)",(body))

print "Starting Giraffe Service"
with daemon.DaemonContext():
    coreService = CoreService()
    coreService.start()

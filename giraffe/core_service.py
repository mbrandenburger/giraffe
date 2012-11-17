__author__ = 'mbrandenburger'

import pika
import MySQLdb as db
import daemon

class QueueListener(object):
    def __init__(self, queueName, exchangeName):
        self.connection = pika.BlockingConnection(pika.ConnectionParameters('cloud'))
        self.channel = self.connection.channel()
        self.exchange = exchangeName
        self.queue = queueName
        
        self.dbconnection = db.connect('sql', 'admin',
                                       'pass', 'tabelle')
    
    def listen(self):
        self.channel.basic_consume(self.callback, no_ack=True,
                                   queue=self.queue)
        self.channel.start_consuming()
    
    def callback(self, ch, method, properties, body):
        print " -> %r:%r" % (method,body,)
        with self.dbconnection:
            cur = self.dbconnection.cursor()
            cur.execute("INSERT INTO compute_log(logging_message) VALUES(%s)",(body))

print "Starting Giraffe Service"
with daemon.DaemonContext():
    service = QueueListener('Giraffe.compute', 'nova')
    service.listen()
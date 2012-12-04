__author__ = 'marcus'

import pika

class Connector(object):
    def __init__(self,host='localhost'):
        self.connection = pika.BlockingConnection(pika.ConnectionParameters(host))
        self.channel = self.connection.channel()

    def getConnection(self):
        return self.connection

    def getChannel(self):
        return self.channel

class BasicConsumer(object):
    def __init__(self, connector, queue, exchange, callback):
        self.connector = connector
        self.channel = connector.channel
        self.exchange = exchange
        self.queue = queue
        self.callback = callback

    def consume(self):
        self.channel.basic_consume(self.callback, no_ack=True, queue=self.queue)
        self.channel.start_consuming()

class BasicProducer(object):

    def __init__(self, connector, exchange):
        self.connector = connector
        self.channel = connector.channel
        self.exchange = exchange

    def send(self,exchange, routing_key, message):
        self.channel.basic_publish(exchange,
            routing_key,
            message,
            properties=pika.BasicProperties(delivery_mode = 2,)
        )
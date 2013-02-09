__author__ = 'marcus'

import time
import pika
import logging
from pika.exceptions import AMQPConnectionError

logger = logging.getLogger("agent")

class Connector(object):
    def __init__(self, username="guest", password="guest", host="localhost",
                 port=5672):
        self.connection = None
        self.parameters = pika.ConnectionParameters(
            host=host,
            port=port,
            credentials=pika.PlainCredentials(username, password)
        )

    def connect(self, reconnection_interval=10):
        try:
            self.connection = pika.BlockingConnection(self.parameters)

        except AMQPConnectionError:
            logger.debug("AMQPConnectionException: %s",
                         AMQPConnectionError)
            time.sleep(reconnection_interval)
        except Exception:
                logger.debug("Error: %s", Exception)

    def getConnection(self):
        return self.connection

    def getChannel(self):
        return self.connection.channel()

    def isConnected(self):
        return self.connection.is_open


class BasicConsumer(object):
    def __init__(self, connector, queue, exchange, callback):
        self.connector = connector
        self.exchange = exchange
        self.queue = queue
        self.callback = callback
        self.isConsuming = False

    def consume(self):
        if not self.isConsuming:
            channel = self.connector.getChannel()
            channel.basic_consume(self._consumer_call,
                                                 no_ack=True,
                                                 queue=self.queue)
            self.isConsuming = True
            channel.start_consuming()

    def stop_consuming(self):
        self.connector.getChannel().stop_consuming()
        self.isConsuming = False

    def _consumer_call(self, ch, method, properties, body):
        self.callback(body)


class BasicProducer(object):
    def __init__(self, connector, exchange):
        self.connector = connector
        self.exchange = exchange

    def send(self, exchange, routing_key, message):
        self.connector.getChannel().basic_publish(exchange,
                                             routing_key,
                                             message,
                                             properties=pika.BasicProperties(
                                                 delivery_mode=2, ))

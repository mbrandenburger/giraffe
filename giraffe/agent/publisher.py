__author__ = 'marcus'

from giraffe.common.rabbit_mq_connector import Connector
from giraffe.common.rabbit_mq_connector import BasicProducer
from giraffe.common.config import *
import logging

logger = logging.getLogger("agent")
config = Config("giraffe.cfg")

_RABBIT_HOST = config.get("rabbit","host")
_RABBIT_QUEUE = config.get("rabbit", "queue")
_RABBIT_EXCHANGE = config.get("rabbit","exchange")
_RABBIT_ROUTING_KEY = config.get("rabbit","routing_key")

class AgentPublisher(object):

    def __init__(self):
        self.connector = Connector(_RABBIT_HOST)
        self.queue = _RABBIT_QUEUE
        self.exchange = _RABBIT_EXCHANGE
        self.routing_key = _RABBIT_ROUTING_KEY
        self.producer = BasicProducer(self.connector, self.exchange)

    def publish(self,params):
        logger.debug("Publish message: %s",params)
        self.producer.send(self.exchange, self.routing_key, params)
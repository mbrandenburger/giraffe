
__author__ = 'marcus'

import logging
import threading
from giraffe.common.config import Config
from giraffe.common.rabbit_mq_connector import Connector, BasicConsumer

logger = logging.getLogger("service.collector")
config = Config("giraffe.cfg")

_RABBIT_HOST = config.get("rabbit","host")
_RABBIT_QUEUE = config.get("rabbit", "queue")
_RABBIT_EXCHANGE = config.get("rabbit","exchange")
_RABBIT_ROUTING_KEY = config.get("rabbit","routing_key")


class Collector(threading.Thread):

    def __init__(self):
        threading.Thread.__init__(self)
        self.connector = Connector(_RABBIT_HOST)
        self.queue = _RABBIT_QUEUE
        self.exchange = _RABBIT_EXCHANGE
        self.routing_key = _RABBIT_ROUTING_KEY
        self.consumer = BasicConsumer(self.connector, self.queue, self.exchange, self._collector_callback)

    def run(self):
        self.start_collecting()

    def stop(self):
        self.stop_collecting()
        self._Thread__stop()

    def start_collecting(self):
        logger.debug("Start collecting from rabbit")
        self.consumer.consume()

    def stop_collecting(self):
        logger.debug("Stop collecting from rabbit")
        self.consumer.stop_consuming()

    def _collector_callback(self,params):
        logger.debug("Collect message: %s",params)
#        (Marcus) TODO: unwrap message and save in database
import threading
import time

__author__ = 'marcus'

from giraffe.common.rabbit_mq_connector import Connector
from giraffe.common.rabbit_mq_connector import BasicProducer
from giraffe.common.config import *
import logging

logger = logging.getLogger("agent")
config = Config("giraffe.cfg")

_RABBIT_HOST = config.get("rabbit", "host")
_RABBIT_QUEUE = config.get("rabbit", "queue")
_RABBIT_EXCHANGE = config.get("rabbit", "exchange")
_RABBIT_ROUTING_KEY = config.get("rabbit", "routing_key")


class AgentPublisher(threading.Thread):

    def __init__(self, agent, duration):
        threading.Thread.__init__(self)
        self.agent = agent
        self.flush_duration = duration
        self.stopRequest = False
        self.connector = Connector(_RABBIT_HOST)
        self.queue = _RABBIT_QUEUE
        self.exchange = _RABBIT_EXCHANGE
        self.routing_key = _RABBIT_ROUTING_KEY
        self.producer = BasicProducer(self.connector, self.exchange)

    def flush(self):
        """
        Sends current state of agents message to the broker.
        """
        if not self.agent.lock.locked():
            self.agent.lock.acquire()
            try:
                if self.agent.message.len() > 0:
                    logger.debug("Flush meter %s" % self.agent.message.len())
                    # flush message
                    self.producer.send(
                        self.exchange, self.routing_key,
                        self.agent.message.serialize_to_str())

                    # build new message
                    self.agent.message = self.agent._build_message()
            finally:
                self.agent.lock.release()

    def run(self):
        while self.stopRequest is False:
            time.sleep(self.flush_duration)
            self.flush()

    def stop(self):
        self.stopRequest = True
        self._Thread__stop()

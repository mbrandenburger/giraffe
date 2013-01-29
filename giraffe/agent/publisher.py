__author__ = 'marcus'

import threading
import time
import logging
from datetime import datetime
from giraffe.common.message_adapter import MessageAdapter
from giraffe.common.rabbit_mq_connector import Connector
from giraffe.common.rabbit_mq_connector import BasicProducer
from giraffe.common.config import *

logger = logging.getLogger("agent")
config = Config("giraffe.cfg")

_RABBIT_HOST = config.get("rabbit", "host")
_RABBIT_QUEUE = config.get("rabbit", "queue")
_RABBIT_EXCHANGE = config.get("rabbit", "exchange")
_RABBIT_ROUTING_KEY = config.get("rabbit", "routing_key")
_FLUSH_DURATION = config.getint("agent", "duration")
_HOSTNAME = config.get("agent", "hostname") # ...considered harmful.
_SIGNATURE = "TODO"


class AgentPublisher(threading.Thread):

    def __init__(self, agent):
        threading.Thread.__init__(self)
        self.agent = agent
        self.flush_duration = _FLUSH_DURATION
        self.stopRequest = False
        self.lock = threading.Lock()
        self.connector = Connector(_RABBIT_HOST)
        self.queue = _RABBIT_QUEUE
        self.exchange = _RABBIT_EXCHANGE
        self.routing_key = _RABBIT_ROUTING_KEY
        self.producer = BasicProducer(self.connector, self.exchange)
        self.message = self._build_message()

    def _timestamp_now(self):
        """
        Returns current system time as formatted string "%Y-%m-%d %H:%M:%S"
        """
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    def _build_message(self):
        """
        Returns a new MessageAdapter object with hostname and signature
        :rtype : MessageAdapter
        """
        message = MessageAdapter()
        message.host_name = _HOSTNAME
        message.signature = _SIGNATURE
        return message

    def add_meter_record(self, meter_name, meter_value, meter_duration):
        """
        Add new meter record to meter message
        Params: meter type [as string], value(s), and duration [in seconds]
        """
        # @[fbahr]: Instead of passing meter_name as a string, either meter
        #           or typed meter values should be returned.
        logger.debug("Add meter record: %s=%s" % (meter_name, meter_value))

        if not self.lock.locked():
            self.lock.acquire()
            try:
                if meter_name.startswith("inst"):
                    #@[fbahr]: Gathering information about project & user id
                    #          ...how/where?
                    for record in meter_value:
                        self.message.add_inst_record(
                            timestamp=record[1],
                            meter_name=meter_name,
                            value=record[2],
                            duration=meter_duration,
                            project_id=None,
                            instance_id=record[0],
                            user_id=None)
                else:
                    self.message.add_host_record(
                        self._timestamp_now(),
                        meter_name,
                        meter_value,
                        meter_duration)
            finally:
                self.lock.release()


    def flush(self):
        """
        Sends current state of agents message to the broker.
        """
        logger.debug("Flush meter message")

        if not self.lock.locked():
            self.lock.acquire()
            try:
                if self.message.len() > 0:
                    # flush message
                    self.producer.send(
                        self.exchange, self.routing_key,
                        self.message.serialize_to_str())

                    # build new message
                    self.message = self._build_message()
            finally:
                self.lock.release()

    def run(self):
        while self.stopRequest is False:
            time.sleep(self.flush_duration)
            self.flush()

    def stop(self):
        self.stopRequest = True
        self._Thread__stop()

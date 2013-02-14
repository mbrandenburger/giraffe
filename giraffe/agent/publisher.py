from giraffe.common.crypto import createSignature
from giraffe.common.envelope_adapter import EnvelopeAdapter

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
_RABBIT_PORT = config.getint("rabbit", "port")
_RABBIT_QUEUE = config.get("rabbit", "queue")
_RABBIT_EXCHANGE = config.get("rabbit", "exchange")
_RABBIT_ROUTING_KEY = config.get("rabbit", "routing_key")
_RABBIT_USER = config.get("rabbit", "user")
_RABBIT_PASS = config.get("rabbit", "pass")
_FLUSH_DURATION = config.getint("agent", "duration")
_HOSTNAME = config.get("agent", "hostname")  # ...considered harmful.
_SHARED_SECRET = config.get("agent", "shared_secret")


class AgentPublisher(threading.Thread):
    def __init__(self, agent):
        threading.Thread.__init__(self)
        self.agent = agent
        self.flush_duration = _FLUSH_DURATION
        self.stopRequest = False
        self.lock = threading.Lock()
        self.connector = Connector(_RABBIT_USER, _RABBIT_PASS, _RABBIT_HOST,
                                   _RABBIT_PORT)
        self.queue = _RABBIT_QUEUE
        self.exchange = _RABBIT_EXCHANGE
        self.routing_key = _RABBIT_ROUTING_KEY
        self.producer = BasicProducer(self.connector, self.exchange)
        self.envelope = self._build_message()

    def _timestamp_now(self, datetime_now=None):
        """
        Returns current system time as formatted string "%Y-%m-%d %H:%M:%S"
        """
        if not datetime_now:
            datetime_now = datetime.now()
        return datetime_now.strftime("%Y-%m-%d %H:%M:%S")

    def _build_message(self):
        """
        Returns a new MessageAdapter object with hostname and signature
        :rtype : MessageAdapter
        """
        envelope = EnvelopeAdapter()

        envelope.message.host_name = _HOSTNAME
        #        message.signature = _SIGNATURE
        return envelope

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
                    for record in meter_value:
                        self.envelope.add_inst_record(
                            timestamp=self._timestamp_now(record[1]),
                            meter_name=meter_name,
                            value=record[2],
                            duration=meter_duration,
                            project_id='',
                            inst_id=record[0],
                            user_id='')
                else:
                    self.envelope.add_host_record(
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
                if self.envelope.len() > 0:
                    # flush message
                    self._send(self.envelope)

                    # build new message
                    self.envelope = self._build_message()

            # except Exception as e:
            #     logger.exception(e)

            finally:
                self.lock.release()

    def _send(self, envelope):
        """
        Create message signature and send envelop to broker
        """
        messageAdapter = MessageAdapter(envelope.message)


        sig = createSignature(str(messageAdapter), _SHARED_SECRET)
        envelope.signature = sig

        self.producer.send(
            self.exchange,
            self.routing_key,
            envelope.serialize_to_str())

    def run(self):
        self.connector.connect()
        while self.stopRequest is False:
            time.sleep(self.flush_duration)
            self.flush()

    def stop(self):
        self.stopRequest = True
        self._Thread__stop()

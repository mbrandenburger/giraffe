__author__ = 'marcus'

import threading
import time

from datetime import datetime

from giraffe.common.message_adapter import MessageAdapter
from giraffe.common.envelope_adapter import EnvelopeAdapter
from giraffe.common.crypto import createSignature
from giraffe.common.rabbit_mq_connector import Connector
from giraffe.common.rabbit_mq_connector import BasicProducer
from giraffe.common.config import Config

import logging
logger = logging.getLogger("agent")


class AgentPublisher(threading.Thread):
    def __init__(self, agent):
        threading.Thread.__init__(self)

        self.agent = agent
        config = Config('giraffe.cfg')
        self.host_name = config.get('agent', 'host_name')

        self.flush_duration = config.getint('agent', 'duration')

        self.connector = Connector(username=config.get('rabbit', 'user'),
                                   password=config.get('rabbit', 'pass'),
                                   host=config.get('rabbit', 'host'),
                                   port=config.getint('rabbit', 'port'))
        self.queue = config.get('rabbit', 'queue')
        self.exchange = config.get('rabbit', 'exchange')
        self.routing_key = config.get('rabbit', 'routing_key')
        self.producer = BasicProducer(self.connector, self.exchange)

        self.shared_secret = config.get('agent', 'shared_secret')
        self.envelope = self._build_message()

        self.stopRequest = False
        self.lock = threading.Lock()

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
        envelope.message.host_name = self.host_name
        #        message.signature = _SIGNATURE
        return envelope

    def add_meter_record(self, meter_name, meter_value, meter_duration):
        """
        Add new meter record to meter message
        Params: meter type [as string], value(s), and duration [in seconds]
        """
        logger.debug("Add meter record: %s=%s" % (meter_name, meter_value))

        if not self.lock.locked():
            self.lock.acquire()
            try:
                if meter_name.startswith('inst'):
                    for record in meter_value:
                        self.envelope.add_inst_record(
                            timestamp=self._timestamp_now(record[1]),
                            meter_name=meter_name,
                            value=record[2],
                            duration=meter_duration,
                            project_id='',
                            inst_id=record[0],
                            user_id='')
                else:  # .startswith('host'):
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
        sig = createSignature(str(messageAdapter), self.shared_secret)
        envelope.signature = sig
        self.producer.send(exchange=self.exchange,
                           routing_key=self.routing_key,
                           message=envelope.serialize_to_str())

    def run(self):
        self.connector.connect()
        while self.stopRequest is False:
            time.sleep(self.flush_duration)
            self.flush()

    def stop(self):
        self.stopRequest = True
        self._Thread__stop()

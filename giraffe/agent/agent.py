__author__ = 'marcus'

import threading
import time
from datetime import datetime

from giraffe.agent.host_meter import Host_CPU_AVG, Host_VIRTMEM_Usage,\
    Host_PHYMEM_Usage
from giraffe.agent import publisher
from giraffe.common.message_adapter import MessageAdapter
from giraffe.common.config import Config

import logging

logger = logging.getLogger("agent")
config = Config("giraffe.cfg")

_FLUSH_DURATION = config.getint("agent", "duration")
_METER_DURATION = int(_FLUSH_DURATION / 4)
_HOSTNAME = config.get("agent", "hostname")
_SIGNATURE = "TODO"


class Agent(object):

    def __init__(self):
        """
        Initializes a new Agent.
        """

        self.lock = threading.Lock()
        self.timer = False
        self.message = self._build_message()
        self.tasks = []

        # meter CPU AVG
        self.tasks.append(
            publisher.AgentPublisher(self, _FLUSH_DURATION)
        )

        # meter CPU AVG
        self.tasks.append(
            Host_CPU_AVG(self._callback_cpu_avg, _METER_DURATION)
        )
        # meter phy memory
        self.tasks.append(
            Host_PHYMEM_Usage(self._callback_phy_mem, _METER_DURATION)
        )

        # meter vir memory
        self.tasks.append(
            Host_VIRTMEM_Usage(self._callback_vir_mem, _METER_DURATION)
        )

    def _build_message(self):
        """
        Returns a new MessageAdapter object with hostname and signature
        :rtype : MessageAdapter
        """
        message = MessageAdapter()
        message.host_name = _HOSTNAME
        message.signature = _SIGNATURE
        return message

    def _timestamp_now(self):
        """
        Returns current system time as formatted string "%Y-%m-%d %H:%M:%S"
        """
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    def _callback_cpu_avg(self, params):
        timestamp = self._timestamp_now()
        if not self.lock.locked():
            self.lock.acquire()
            try:
                logger.debug("Meter message: loadavg_1m=%s" % params[0])
                self.message.add_host_record(
                    timestamp, 'loadavg_1m', params[0], 60)

                logger.debug("Meter message: loadavg_5m=%s" % params[1])
                self.message.add_host_record(
                    timestamp, 'loadavg_5m', params[1], 300)

                logger.debug("Meter message: loadavg_1mm=%s" % params[2])
                self.message.add_host_record(
                    timestamp, 'loadavg_15m', params[2], 1500)
            finally:
                self.lock.release()

    def _callback_phy_mem(self, params):
        timestamp = self._timestamp_now()
        if not self.lock.locked():
            self.lock.acquire()
            try:
                logger.debug("Meter message: phymem_usage=%s" % params[3])
                self.message.add_host_record(
                    timestamp, 'phymem_usage', params[3], 0)
            finally:
                self.lock.release()

    def _callback_vir_mem(self, params):
        timestamp = self._timestamp_now()
        if not self.lock.locked():
            self.lock.acquire()
            try:
                logger.debug("Meter message: virmem_usage=%s" % params[3])
                self.message.add_host_record(
                    timestamp, 'virmem_usage', params[3], 0)
            finally:
                self.lock.release()

    def launch(self):
        """
        Starts all publisher and all meter tasks.
        """
        global logger
        try:
            # start all meter
            for t in self.tasks:
                t.start()

            # run
            while threading.active_count() > 0:
                time.sleep(0.1)

        except KeyboardInterrupt:
            logger.info("Ctrl-c received! Sending stop agent")
            for t in self.tasks:
                t.stop()
        except:
            logger.exception("Error: unable to start agent")
        finally:
            logger.info("Exiting Agent")

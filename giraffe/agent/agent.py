__author__ = 'marcus'

import threading
import time
from datetime import datetime

from giraffe.agent.host_meter import Host_CPU_AVG
from giraffe.agent import publisher
from giraffe.common.message_adapter import MessageAdapter
from giraffe.common.config import Config

import logging

logger = logging.getLogger("agent")
config = Config("giraffe.cfg")

_DURATION = config.getint("agent", "duration")


class Agent(object):

    def __init__(self):
        self.publisher = publisher.AgentPublisher()
        self.meterTasks = []

        # meter CPU AVG
        self.meterTasks.append(Host_CPU_AVG(self._callback_cpu_avg, _DURATION))

    def _timestamp_now(self):
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    def _callback_cpu_avg(self, params):
        #message = MessageAdapter.host_cpu_avg(params)
        message = MessageAdapter()
        message.host_id = config.get("agent", "hostname")
        message.signature = 'TODO'
        timestamp = self._timestamp_now()
        message.add_host_record(timestamp, 'loadavg_1m', params[0], 60)
        message.add_host_record(timestamp, 'loadavg_5m', params[1], 300)
        message.add_host_record(timestamp, 'loadavg_15m', params[2], 1500)
        self.publisher.publish(message.serialize_to_str())

    def launch(self):
        global logger
        try:
            for t in self.meterTasks:
                t.start()

            while threading.active_count() > 0:
                time.sleep(0.1)

        except KeyboardInterrupt:
            logger.info("Ctrl-c received! Sending stop agent")
            for t in self.meterTasks:
                t.stop()
        except:
            logger.exception("Error: unable to start agent")
        finally:
            logger.info("Exiting Agent")

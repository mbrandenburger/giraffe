__author__ = 'marcus'

import threading
import time
from giraffe.agent.host_meter import Host_CPU_AVG
from giraffe.agent import publisher
from giraffe.common.message_adapter import MessageAdapter
from giraffe.common.config import Config

import logging

logger = logging.getLogger("agent")
config = Config("giraffe.cfg")

_DURATION = config.getint("agent","duration")

class Agent(object):

    def __init__(self):
        self.publisher = publisher.AgentPublisher()
        self.meterTasks = []

        # meter CPU AVG
        self.meterTasks.append(Host_CPU_AVG(self._callback_cpu_avg, _DURATION))

    def _callback_cpu_avg(self, params):
        message = MessageAdapter.host_cpu_avg(params)
        self.publisher.publish(message)

    def launch(self):
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
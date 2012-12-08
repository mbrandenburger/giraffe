

__author__ = 'marcus'

from giraffe.agent import host_meter
from giraffe.agent import publisher
from giraffe.common.message_adapter import MessageAdapter
from giraffe.common import task
from giraffe.common.config import Config

import logging

logger = logging.getLogger("agent")
config = Config("giraffe.cfg")

_HOSTNAME = config.get("agent","hostname")
_DURATION = config.getint("agent","duration")

class Agent(object):

    def __init__(self):
        self.publisher = publisher.AgentPublisher()
        self.meter = []
        self._registerMeter(host_meter.Host_CPU_AVG(_DURATION, self._callback_cpu_avg))
        
    def _callback_cpu_avg(self, params):
        message = MessageAdapter.host_cpu_avg(params)
        self.publisher.publish(message)

    def _registerMeter(self, meter):
        self.meter.append(meter)

    def launch(self):
        for meter in self.meter:
            task.Launcher(meter)

#if __name__ == '__main__':
#
#    agent = Agent()
#    agent.registerMeter(host_meter.Host_CPU_AVG(DURATION, _callback_cpu_avg))
#    agent.registerMeter(HostMeter.Host_UNAME(30, callback_uname))
#    agent.registerMeter(HostMeter.Host_VIRTMEM_Usage(20, callback_virtmem_usage))
#    agent.registerMeter(HostMeter.Host_PHYMEM_Usage(1, callback_phymem_usage))
#
#    agent.launch()

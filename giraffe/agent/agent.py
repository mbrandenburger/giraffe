from giraffe.agent.DataWrapper import Wrapper
from giraffe.common.RabbitMQConnector import Connector, BasicProducer

__author__ = 'marcus'

from giraffe.common import Service, HostMeter

HOSTNAME = 'Macbook'
DURATION = 1
RABBIT_EXCHANGE = 'giraffe_topic'

def _callback_cpu_avg(params):
    message = Wrapper.host_cpu_avg(params)
    print message
    agent.producer.send(RABBIT_EXCHANGE,'',message)

class Agent(object):

    def __init__(self):
        self.connector = Connector('cloud2.ibr.cs.tu-bs.de')
        self.producer = BasicProducer(self.connector, RABBIT_EXCHANGE)
        self.meter = []

    def registerMeter(self, meter):
        self.meter.append(meter)

    def launch(self):
        for meter in self.meter:
            Service.Launcher(meter)

if __name__ == '__main__':

    agent = Agent()
    agent.registerMeter(HostMeter.Host_CPU_AVG(DURATION, _callback_cpu_avg))
#    agent.registerMeter(HostMeter.Host_UNAME(30, callback_uname))
#    agent.registerMeter(HostMeter.Host_VIRTMEM_Usage(20, callback_virtmem_usage))
#    agent.registerMeter(HostMeter.Host_PHYMEM_Usage(1, callback_phymem_usage))

    agent.launch()


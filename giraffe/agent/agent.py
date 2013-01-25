__author__ = 'marcus'

import threading
import time
import logging
from giraffe.agent.host_meter import Host_CPU_AVG, Host_VIRMEM_Usage, \
    Host_PHYMEM_Usage, Host_UPTIME, Host_NETWORK_IO
from giraffe.agent.instance_meter import Inst_CPU_Usage, Inst_VIRMEM_Usage, \
    Inst_PHYMEM_Usage, Inst_UPTIME, Inst_NETWORK_IO
from giraffe.agent import publisher
from giraffe.common.config import Config

logger = logging.getLogger("agent")
config = Config("giraffe.cfg")

_FLUSH_DURATION = config.getint("agent", "duration")
_METER_DURATION = int(_FLUSH_DURATION / 4)


class Agent(object):

    def __init__(self):
        """
        Initializes a new Agent.
        """
        self.timer = False
        self.tasks = []
        self.publisher = publisher.AgentPublisher(self)

        # add publisher to tasks
        self.tasks.append(
            self.publisher
        )

        # HOST METERS ---------------------------------------------------------

        # meter host CPU AVG
        self.tasks.append(
            Host_CPU_AVG(self._callback_cpu_avg, _METER_DURATION)
        )

        # meter host phy memory
        self.tasks.append(
            Host_PHYMEM_Usage(self._callback_phy_mem, _METER_DURATION)
        )

        # meter host vir memory
        self.tasks.append(
            Host_VIRMEM_Usage(self._callback_vir_mem, _METER_DURATION)
        )

        # meter host uptime
        self.tasks.append(
            Host_UPTIME(self._callback_uptime, _METER_DURATION)
        )

        # meter host network io
        self.tasks.append(
            Host_NETWORK_IO(self._callback_network_io, _METER_DURATION)
        )

        # INSTANCE METERS -----------------------------------------------------

        # meter instance phy memory
        self.tasks.append(
            Inst_PHYMEM_Usage(self._callback_inst_phy_mem, _METER_DURATION)
        )

        # meter instances vir memory
        self.tasks.append(
            Inst_VIRMEM_Usage(self._callback_inst_vir_mem, _METER_DURATION)
        )

        # meter instances uptime
        self.tasks.append(
            Inst_UPTIME(self._callback_inst_uptime, _METER_DURATION)
        )


    # CB METHODS FOR HOST METERS ----------------------------------------------

    def _callback_cpu_avg(self, params):
        self.publisher.add_meter_record('loadavg_1m', params[0], 60)
        self.publisher.add_meter_record('loadavg_5m', params[1], 300)
        self.publisher.add_meter_record('loadavg_15m', params[2], 1500)

    def _callback_phy_mem(self, params):
        self.publisher.add_meter_record('phymem_usage', params[3], 0)

    def _callback_vir_mem(self, params):
        self.publisher.add_meter_record('virmem_usage', params[3], 0)

    def _callback_uptime(self, params):
        self.publisher.add_meter_record('uptime', params, 0)

    def _callback_network_io(self, params):
        self.publisher.add_meter_record('network_io_tx', params[0], 0)
        self.publisher.add_meter_record('network_io_rx', params[1], 0)


    # CB METHODS FOR INSTANCE METERS ------------------------------------------

    def _callback_inst_phy_mem(self, params):
        self.publisher.add_meter_record('inst_phymem_usage', params, 0)
        # self.publisher.add_meter_record('inst_phymem_usage', params[3], 0)

    def _callback_inst_vir_mem(self, params):
        self.publisher.add_meter_record('inst_virmem_usage', params, 0)
        # self.publisher.add_meter_record('inst_virmem_usage', params[3], 0)

    def _callback_inst_uptime(self, params):
        self.publisher.add_meter_record('inst_uptime', params, 0)


    # -------------------------------------------------------------------------

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

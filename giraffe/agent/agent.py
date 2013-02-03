__author__ = 'marcus, fbahr'

import threading
import time
import logging
from giraffe.agent.host_meter import Host_CPU_AVG, Host_VIRMEM_Usage, \
                                     Host_PHYMEM_Usage, Host_UPTIME, \
                                     Host_NETWORK_IO
from giraffe.agent.inst_meter import Inst_CPU, Inst_VIRMEM, Inst_PHYMEM, \
                                     Inst_UPTIME, Inst_DISK_IO, \
                                     Inst_NETWORK_IO
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

        # meter host network I/O
        self.tasks.append(
            Host_NETWORK_IO(self._callback_network_io, _METER_DURATION)
        )

        # INSTANCE METERS -----------------------------------------------------

        # meter instance cpu utilization
        self.tasks.append(
            Inst_CPU(self._callback_inst_cpu, _METER_DURATION)
        )

        # meter instance phy memory
        self.tasks.append(
            Inst_PHYMEM(self._callback_inst_phy_mem, _METER_DURATION)
        )

        # meter instance vir memory
        self.tasks.append(
            Inst_VIRMEM(self._callback_inst_vir_mem, _METER_DURATION)
        )

        # meter instance uptime
        self.tasks.append(
            Inst_UPTIME(self._callback_inst_uptime, _METER_DURATION)
        )

        # meter instance disk I/O
        self.tasks.append(
            Inst_DISK_IO(self._callback_inst_disk_io, _METER_DURATION)
        )

    # CB METHODS FOR HOST METERS ----------------------------------------------

    def _callback_cpu_avg(self, params):
        self.publisher.add_meter_record('host.loadavg_1m', params[0], 60)
        self.publisher.add_meter_record('host.loadavg_5m', params[1], 300)
        self.publisher.add_meter_record('host.loadavg_15m', params[2], 1500)

    def _callback_phy_mem(self, params):
        self.publisher.add_meter_record('host.phymem_usage', params[3], 0)

    def _callback_vir_mem(self, params):
        self.publisher.add_meter_record('host.virmem_usage', params[3], 0)

    def _callback_uptime(self, params):
        self.publisher.add_meter_record('host.uptime', params, 0)

    def _callback_network_io(self, params):
        self.publisher.add_meter_record('host.network.io.outgoing.bytes', params[0], 0)
        self.publisher.add_meter_record('host.network.io.incoming.bytes', params[1], 0)

    # CB METHODS FOR INSTANCE METERS ------------------------------------------

    def _callback_inst_cpu(self, params):
        zipped_params = zip(*params)
        descriptors = zipped_params[0:2]  # uuids and timestamps
        self.publisher.add_meter_record(
                            'inst.cpu.time',
                            zip(*(descriptors + [zipped_params[2]])),
                            0)
        self.publisher.add_meter_record(
                            'inst.cpu.time.ratio',
                            zip(*(descriptors + [zipped_params[3]])),
                            0)
        self.publisher.add_meter_record(
                            'inst.cpu.percent',
                            zip(*(descriptors + [zipped_params[4]])),
                            0)

    def _callback_inst_phy_mem(self, params):
        self.publisher.add_meter_record('inst.memory.physical', params, 0)

    def _callback_inst_vir_mem(self, params):
        self.publisher.add_meter_record('inst.memory.virtual', params, 0)

    def _callback_inst_uptime(self, params):
        self.publisher.add_meter_record('inst.uptime', params, 0)

    def _callback_inst_disk_io(self, params):
        zipped_params = zip(*params)
        descriptors = zipped_params[0:2]  # uuids and timestamps
        self.publisher.add_meter_record(
                            'inst.disk.io.read.requests',
                            # zip(*(descriptors + [zip(*zipped_params)[0]])),
                            zip(*(descriptors + [zipped_params[2]])),
                            0)
        self.publisher.add_meter_record(
                            'inst.disk.io.read.bytes',
                            # zip(*(descriptors + [zip(*zipped_params)[1]])),
                            zip(*(descriptors + [zipped_params[3]])),
                            0)
        self.publisher.add_meter_record(
                            'inst.disk.io.write.requests',
                            # zip(*(descriptors + [zip(*zipped_params)[2]])),
                            zip(*(descriptors + [zipped_params[4]])),
                            0)
        self.publisher.add_meter_record(
                            'inst.disk.io.write.bytes',
                            # zip(*(descriptors + [zip(*zipped_params)[3]])),
                            zip(*(descriptors + [zipped_params[5]])),
                            0)

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

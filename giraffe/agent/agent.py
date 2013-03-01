__author__ = 'mbrandenburger, fbahr'

import threading
import time
from giraffe.agent.host_meter \
    import Host_UPTIME, Host_CPU_Load, Host_MEMORY_Usage, \
           Host_DISK_IO, Host_NETWORK_IO
from giraffe.agent.instance_meter \
    import Inst_CPU_Time, Inst_VIRMEM_Usage, Inst_PHYMEM_Usage, Inst_UPTIME, \
           Inst_DISK_IO, Inst_NETWORK_IO
from giraffe.agent import publisher
from giraffe.common.config import Config

import logging
logger = logging.getLogger('agent')


class Agent(object):

    HOST_METER = {'host_uptime': Host_UPTIME,
                  'host_cpu_load': Host_CPU_Load,
                  'host_memory_usage': Host_MEMORY_Usage,
    #             'host_phymem_usage': Host_PHYMEM_Usage,
    #             'host_virmem_usage': Host_VIRMEM_Usage,
                  'host_disk_io': Host_DISK_IO,
                  'host_network_io': Host_NETWORK_IO}

    INST_METER = {'inst_uptime': Inst_UPTIME,
                  'inst_cpu_time': Inst_CPU_Time,
                  'inst_phymem_usage': Inst_PHYMEM_Usage,
                  'inst_virmem_usage': Inst_VIRMEM_Usage,
                  'inst_disk_io': Inst_DISK_IO,
                  'inst_network_io': Inst_NETWORK_IO}

    def __init__(self, cfg=None):
        """
        Initializes a new Agent.
        """

        # fetch config parameters
        config = Config(cfg if cfg else 'giraffe.cfg')

        # configure agent
        self.timer = False
        self.tasks = []
        self.publisher = publisher.AgentPublisher(self)

        # add publisher to tasks
        self.tasks.append(self.publisher)

        # HOST METERS ---------------------------------------------------------

        meters = config.items('agent')
        for (meter, value) in meters:
            try:
                if self.HOST_METER.get(meter):
                    self.tasks.append(self.HOST_METER[meter](
                                        getattr(self, '_callback_' + meter),
                                        int(value)))
            except ValueError:
                logging.exception('Host meter %s ommitted due to ValueError: '
                                  '\'%s\' is not of type \'int\'' % (meter, value))

        # uptime = config.get('agent', 'host_uptime')
        # cpu_load = config.get('agent', 'host_cpu_load')
        # mem_usage = config.get('agent', 'host_memory_usage')
        # disk_io = config.get('agent', 'host_disk_io')
        # network_io = config.get('agent', 'host_network_io')

        # host meter `uptime`
        # if uptime:
        #     self.tasks.append(Host_UPTIME(
        #                         self._callback_host_uptime,
        #                         int(uptime)))

        # host meter `CPU load`
        # if cpu_load:
        #     self.tasks.append(Host_CPU_Load(
        #                         self._callback_host_cpu_load,
        #                         int(loadavg)))

        # host meter `memory`
        # if mem_usage:
        #     self.tasks.append(Host_MEMORY_Usage(
        #                         self._callback_host_memory_usage,
        #                         int(mem_usage)))

        # host meter `network I/O`
        # if network_io:
        #     self.tasks.append(Host_NETWORK_IO(
        #                         self._callback_host_network_io,
        #                         int(network_io)))

        # INSTANCE METERS -----------------------------------------------------

        for (meter, value) in meters:
            try:
                if self.INST_METER.get(meter):
                    self.tasks.append(self.INST_METER[meter](
                                        getattr(self, '_callback_' + meter),
                                        int(value)))
            except ValueError:
                logging.exception('Instance meter %s ommitted due to ValueError: '
                                  '\'%s\' is not of type \'int\'' % (meter, value))

        # uptime = config.get('agent', 'inst_uptime')
        # cpu_time = config.get('agent', 'inst_cpu_time')
        # phymem_usage = config.get('agent', 'inst_phymem_usage')
        # virmem_usage = config.get('agent', 'inst_virmem_usage')
        # disk_io = config.get('agent', 'inst_disk_io')
        # network_io = config.get('agent', 'inst_network_io')

        # instance meter `uptime`
        # if uptime:
        #     self.tasks.append(Inst_UPTIME(
        #                         self._callback_inst_uptime,
        #                         int(uptime)))

        # instance meter `cpu time`
        # if cpu_time:
        #     self.tasks.append(Inst_CPU_Time(
        #                         self._callback_inst_cpu_time,
        #                         int(cpu_time)))

        # instance meter `phy mem`
        # if phymem_usage:
        #     self.tasks.append(Inst_PHYMEM_Usage(
        #                         self._callback_inst_phy_mem,
        #                         int(phymem_usage)))

        # instance meter `vir mem`
        # if virmem_usage:
        #     self.tasks.append(Inst_VIRMEM_Usage(
        #                         self._callback_inst_vir_mem,
        #                         int(virmem_usage)))

        # instance meter `disk I/O`
        # if disk_io:
        #     self.tasks.append(Inst_DISK_IO(
        #                         self._callback_inst_disk_io,
        #                         int(disk_io)))

        # instance meter `network I/O`
        # if network_io:
        #     self.tasks.append(Inst_NETWORK_IO(
        #                         self._callback_inst_network_io,
        #                         int(network_io)))

    # CALLBACK METHODS FOR HOST METERS ----------------------------------------

    def _callback_host_uptime(self, params):
        self.publisher.add_meter_record(
                       meter_name='host.uptime',
                       meter_value=params,
                       meter_duration=0)

    def _callback_host_cpu_load(self, params):
        self.publisher.add_meter_record(
                       meter_name='host.loadavg_1m',
                       meter_value=params[0],
                       meter_duration=60)
        self.publisher.add_meter_record(
                       meter_name='host.loadavg_5m',
                       meter_value=params[1],
                       meter_duration=300)
        self.publisher.add_meter_record(
                       meter_name='host.loadavg_15m',
                       meter_value=params[2],
                       meter_duration=1500)

    def _callback_host_memory_usage(self, params):
        self.publisher.add_meter_record(
                       meter_name='host.phymem_usage',
                       meter_value=params[0] - params[1],
                       meter_duration=0)
        self.publisher.add_meter_record(
                       meter_name='host.virmem_usage',
                       meter_value=params[5],
                       meter_duration=0)

    def _callback_host_disk_io(self, params):
        pass

    def _callback_host_network_io(self, params):
        self.publisher.add_meter_record(
                       meter_name='host.network.io.outgoing.bytes',
                       meter_value=params[0],
                       meter_duration=0)
        self.publisher.add_meter_record(
                       meter_name='host.network.io.incoming.bytes',
                       meter_value=params[1],
                       meter_duration=0)

    # CALLBACK METHODS FOR INSTANCE METERS ------------------------------------

    def _callback_inst_uptime(self, params):
        self.publisher.add_meter_record(
                       meter_name='inst.uptime',
                       meter_value=params,
                       meter_duration=0)

    def _callback_inst_cpu_time(self, params):
        zipped_params = zip(*params)
        descriptors = zipped_params[0:2]  # uuids and timestamps
        self.publisher.add_meter_record(
                       meter_name='inst.cpu.time',
                       meter_value=zip(*(descriptors + [zipped_params[2]])),
                       meter_duration=0)
        self.publisher.add_meter_record(
                       meter_name='inst.cpu.time.ratio',
                       meter_value=zip(*(descriptors + [zipped_params[3]])),
                       meter_duration=0)
        self.publisher.add_meter_record(
                       meter_name='inst.cpu.percent',
                       meter_value=zip(*(descriptors + [zipped_params[4]])),
                       meter_duration=0)

    def _callback_inst_phymem_usage(self, params):
        self.publisher.add_meter_record(
                       meter_name='inst.memory.physical',
                       meter_value=params,
                       meter_duration=0)

    def _callback_inst_virmem_usage(self, params):
        self.publisher.add_meter_record(
                       meter_name='inst.memory.virtual',
                       meter_value=params,
                       meter_duration=0)

    def _callback_inst_disk_io(self, params):
        zipped_params = zip(*params)
        descriptors = zipped_params[0:2]  # uuids and timestamps
        self.publisher.add_meter_record(
                       meter_name='inst.disk.io.read.requests',
                       meter_value=zip(*(descriptors + [zipped_params[2]])),
                       meter_duration=0)
        self.publisher.add_meter_record(
                       meter_name='inst.disk.io.read.bytes',
                       meter_value=zip(*(descriptors + [zipped_params[3]])),
                       meter_duration=0)
        self.publisher.add_meter_record(
                       meter_name='inst.disk.io.write.requests',
                       meter_value=zip(*(descriptors + [zipped_params[4]])),
                       meter_duration=0)
        self.publisher.add_meter_record(
                       meter_name='inst.disk.io.write.bytes',
                       meter_value=zip(*(descriptors + [zipped_params[5]])),
                       meter_duration=0)

    def _callback_inst_network_io(self, params):
        zipped_params = zip(*params)
        descriptors = zipped_params[0:2]  # uuids and timestamps
        self.publisher.add_meter_record(
                       meter_name='inst.network.io.incoming.bytes',
                       meter_value=zip(*(descriptors + [zipped_params[2]])),
                       meter_duration=0)
        self.publisher.add_meter_record(
                       meter_name='inst.network.io.incoming.packets',
                       meter_value=zip(*(descriptors + [zipped_params[3]])),
                       meter_duration=0)
        self.publisher.add_meter_record(
                       meter_name='inst.network.io.outgoing.bytes',
                       meter_value=zip(*(descriptors + [zipped_params[4]])),
                       meter_duration=0)
        self.publisher.add_meter_record(
                       meter_name='inst.network.io.outgoing.packets',
                       meter_value=zip(*(descriptors + [zipped_params[5]])),
                       meter_duration=0)

    # -------------------------------------------------------------------------

    def launch(self):
        """
        Starts all publisher and meter tasks.
        """

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

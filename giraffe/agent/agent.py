__author__ = 'marcus, fbahr'

import threading
import time
from giraffe.agent.host_meter \
    import Host_UPTIME, Host_CPU_Load, Host_VIRMEM_Usage, Host_PHYMEM_Usage, \
           Host_DISK_IO, Host_NETWORK_IO
from giraffe.agent.instance_meter \
    import Inst_CPU, Inst_VIRMEM, Inst_PHYMEM, Inst_UPTIME, Inst_DISK_IO, \
           Inst_NETWORK_IO
from giraffe.agent import publisher
from giraffe.common.config import Config

import logging
logger = logging.getLogger('agent')


class Agent(object):

    HOST_METER = {'host_uptime': Host_UPTIME,
                  'host_cpu_load': Host_CPU_Load,
                  'host_phymem_usage': Host_PHYMEM_Usage,
                  'host_virmem_usage': Host_VIRMEM_Usage,
                  'host_disk_io': Host_DISK_IO,
                  'host_network_io': Host_NETWORK_IO}

    def __init__(self, config=None):
        """
        Initializes a new Agent.
        """

        # fetch config parameters
        config = Config(config if config else 'giraffe.cfg')

        # configure agent
        self.timer = False
        self.tasks = []
        self.publisher = publisher.AgentPublisher(self)

        # add publisher to tasks
        self.tasks.append(self.publisher)

        # METERS --------------------------------------------------------------

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

        # HOST METERS ---------------------------------------------------------

        # uptime = config.get('agent', "host_uptime", None)
        # loadavg = config.get('agent', "host_loadavg", None)
        # phymem_usage = config.get('agent', "host_phymem_usage", None)
        # virmem_usage = config.get('agent', "host_virmem_usage", None)
        # disk_io = config.get('agent', "host_disk_io", None)
        # network_io = config.get('agent', "host_network_io", None)

        # meter host `uptime`
        # if uptime:
        #     self.tasks.append(Host_UPTIME(
        #                         self._callback_uptime,
        #                         int(uptime)))

        # meter host `CPU load`
        # if loadavg:
        #     self.tasks.append(Host_CPU_Load(
        #                         self._callback_cpu_avg,
        #                         int(loadavg)))

        # meter host `phy mem`
        # if phymem_usage:
        #     self.tasks.append(Host_PHYMEM_Usage(
        #                         self._callback_phy_mem,
        #                         int(phymem_usage)))

        # meter host `vir mem`
        # if virmem_usage:
        #     self.tasks.append(Host_VIRMEM_Usage(
        #                         self._callback_vir_mem,
        #                         int(virmem_usage)))

        # meter host `network I/O`
        # if network_io:
        #     self.tasks.append(Host_NETWORK_IO(
        #                         self._callback_network_io,
        #                         int(network_io)))

        # INSTANCE METERS -----------------------------------------------------

        # meter instance cpu utilization
        self.tasks.append(
            Inst_CPU(self._callback_inst_cpu,
                     config.getint('agent', "inst_cpu"))
        )

        # meter instance phy memory
        self.tasks.append(
            Inst_PHYMEM(self._callback_inst_phy_mem,
                        config.getint('agent', "inst_memory_physical"))
        )

        # meter instance vir memory
        self.tasks.append(
            Inst_VIRMEM(self._callback_inst_vir_mem,
                        config.getint('agent', "inst_memory_virtual"))
        )

        # meter instance uptime
        self.tasks.append(
            Inst_UPTIME(self._callback_inst_uptime,
                        config.getint('agent', "inst_uptime"))
        )

        # meter instance disk I/O
        self.tasks.append(
            Inst_DISK_IO(self._callback_inst_disk_io,
                         config.getint('agent', "inst_disk_io"))
        )

        # meter instance network I/O
        self.tasks.append(
            Inst_NETWORK_IO(self._callback_inst_network_io,
                            config.getint('agent', "inst_network_io"))
        )

    # CALLBACK METHODS FOR HOST METERS ----------------------------------------

    def _callback_host_uptime(self, params):
        self.publisher.add_meter_record(meter_name='host.uptime',
                                        meter_value=params,
                                        meter_duration=0)

    def _callback_host_cpu_load(self, params):
        self.publisher.add_meter_record(meter_name='host.loadavg_1m',
                                        meter_value=params[0],
                                        meter_duration=60)
        self.publisher.add_meter_record(meter_name='host.loadavg_5m',
                                        meter_value=params[1],
                                        meter_duration=300)
        self.publisher.add_meter_record(meter_name='host.loadavg_15m',
                                        meter_value=params[2],
                                        meter_duration=1500)

    def _callback_host_phymem_usage(self, params):
        self.publisher.add_meter_record(meter_name='host.phymem_usage',
                                        meter_value=params[3],
                                        meter_duration=0)

    def _callback_host_virmem_usage(self, params):
        self.publisher.add_meter_record(meter_name='host.virmem_usage',
                                        meter_value=params[3],
                                        meter_duration=0)

    def _callback_host_disk_io(self, params):
        print 'hello'
        pass

    def _callback_host_network_io(self, params):
        self.publisher.add_meter_record(meter_name='host.network.io.outgoing.bytes',
                                        meter_value=params[0],
                                        meter_duration=0)
        self.publisher.add_meter_record(meter_name='host.network.io.incoming.bytes',
                                        meter_value=params[1],
                                        meter_duration=0)

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

    def _callback_inst_network_io(self, params):
        zipped_params = zip(*params)
        descriptors = zipped_params[0:2]  # uuids and timestamps
        self.publisher.add_meter_record(
            'inst.network.io.incoming.bytes',
            zip(*(descriptors + [zipped_params[2]])),
            0)
        self.publisher.add_meter_record(
            'inst.network.io.incoming.packets',
            zip(*(descriptors + [zipped_params[3]])),
            0)
        self.publisher.add_meter_record(
            'inst.network.io.outgoing.bytes',
            zip(*(descriptors + [zipped_params[4]])),
            0)
        self.publisher.add_meter_record(
            'inst.network.io.outgoing.packets',
            zip(*(descriptors + [zipped_params[5]])),
            0)

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

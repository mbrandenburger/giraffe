__author__ = 'marcus, fbahr'

"""
In giraffe (as known from ceilometer), three type of meters are defined:

----------  -------------------------------------------------------------------
Type        Definition
----------  -------------------------------------------------------------------
Cumulative  Increasing over time (e.g., instance hours)
Gauge       Discrete items (e.g., running instances)
            and fluctuating values (e.g., disk I/O)
Delta       Changing over time (bandwidth)
----------  -------------------------------------------------------------------


Meters (by components) that are currently implemented:

Instance [Compute / Nova]
--------------------------------  -------------  ----------  ----------  ------
Name                              Type           Volume      Resource    Note
--------------------------------  -------------  ----------  ----------  ------
inst.uptime                       Gauge          <seconds!>     inst ID  Duration of instance
inst.memory.physical              Gauge            <bytes!>     inst ID  Volume of RAM in <bytes!>
inst.memory.virtual               Gauge            <bytes!>     inst ID  Volume of RAM in <bytes!>
inst.cpu.time                     Cumulative             ms     inst ID  CPU time used
inst.cpu.time.ratio               Gauge             percent     inst ID  CPU time used in relation to real time elapsed
inst.cpu.percent                  Gauge             percent     inst ID  ...
* vcpus                           Gauge                cpus     inst ID  Number of VCPUs
* disk.root.size                  Gauge                  GB     inst ID  Size of root disk in GB
* disk.ephemeral.size             Gauge                  GB     inst ID  Size of ephemeral disk in GB
- inst.disk.io.requests           Cumulative       requests     inst ID  Number of disk io requests
inst.disk.io.read.requests        Cumulative       requests     inst ID  Number of disk I/O read requests
inst.disk.io.write.requests       Cumulative       requests     inst ID  Number of disk I/O write requests
- inst.disk.io.bytes              Cumulative          bytes     inst ID  Volume of disk io in bytes
inst.disk.io.read.bytes           Cumulative          bytes     inst ID  Volume of disk I/O read requests
inst.disk.io.write.bytes          Cumulative          bytes     inst ID  Volum of disk I/O write requests
inst.network.io.incoming.bytes    Cumulative          bytes  <inst ID!>  number of incoming bytes on the network
inst.network.io.outgoing.bytes    Cumulative          bytes  <inst ID!>  number of outgoing bytes on the network
inst.network.io.incoming.packets  Cumulative        packets  <inst ID!>  number of incoming packets
inst.network.io.outgoing.packets  Cumulative        packets  <inst ID!>  number of outgoing packets
--------------------------------  -------------  ----------  ----------  ------


Naming convention
-----------------
If you plan on adding meters, please follow the convention bellow:

1. Always use '.' as separator and go from least to most discriminent word.
   For example, do not use ephemeral_disk_size but disk.ephemeral.size

2. When a part of the name is a variable, it should always be at the end and
   start with a ':'. For example do not use <type>.image but image:<type>, 
   where type is your variable name.


-------------------------------------------------------------------------------
3rd-party modules/dependencies
-------------------------------------------------------------------------------
psutil
libvirt
-------------------------------------------------------------------------------
"""

import sys
import time
from datetime import datetime
import subprocess
from xml.etree import ElementTree as ETree

import psutil
# try:
#     from nova.virt import driver
# except ImportError:
import libvirt
_LIBVIRT_SOCKET_URL = 'qemu:///system'

from giraffe.common.task import PeriodicMeterTask

from novaclient.v1_1.client import Client as NovaClient
from giraffe.common.auth import AuthProxy
from giraffe.common.config import Config
_config = Config('giraffe.cfg')

import logging
logger = logging.getLogger("agent.instance_meter")
# logger.setLevel(logging.DEBUG)
# formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
# fh = logging.FileHandler("agent.log")
# fh.setFormatter(formatter)
# logger.addHandler(fh)


class PeriodicInstMeterTask(PeriodicMeterTask):

    def __init__(self, callback, period):
        super(PeriodicInstMeterTask, self).__init__(callback, period)

        self.conn = libvirt.openReadOnly(_LIBVIRT_SOCKET_URL)
        if not self.conn:
            logger.exception('PeriodicInstMeterTask: '
                             'Failed to open connection to hypervisor.')
            sys.exit(1)

    def _get_inst_ids(self, pids=True):
        """
        Returns a dict of (uuid: (pid, instance-name)) elements for instances
        running on a certain host.
        """
        ids = {}

        try:
            # dict of (uuid: None) elements,
            # in short: instances running on a host
            for domain_id in self.conn.listDomainsID():
                ids[self.conn.lookupByID(domain_id).UUIDString()] = None

# Nova client...
#
#           _credentials = dict(username=_config.get('agent', 'user'),
#                               password=_config.get('agent', 'pass'),
#                               tenant_id=_config.get('agent', 'tenant_id'),
#                               tenant_name=_config.get('agent', 'tenant_name'),
#                               auth_url=_config.get('auth', 'admin_url'),
#                               insecure=True)
#
#           self.nova_client = NovaClient(username=_credentials['username'],
#                                         api_key=_credentials['password'],
#                                         project_id=_credentials['tenant_name'],
#                                         auth_url=_credentials['auth_url'],
#                                         service_type='compute',
#                                         insecure=True)
#
#           _credentials['api_key'] = AuthProxy.get_token(**_credentials)
#           self.nova_client.client.auth_token = _credentials['api_key']
#           self.nova_client.client.authenticate()
#           servers = self.nova_client.servers.find(id=...)

            if not pids:
                return ids

            # CLI 'magic' to grep pids and instance_names, 
            # as initially introduced by marcus
            cmd = "| ".join(["ps -eo pid,command ",
                             "grep uuid ",
                             "grep -v grep ",
                             "grep '"
                             + "\|".join(ids.keys())
                             + "' ",
                             "awk '{print $1, $12, $14}'"])

            # tabular = list of [pid, instance-name, uuid] elements/rows
            tabular = subprocess.check_output(cmd, shell=True) \
                                .decode('ascii')[:-1] \
                                .split('\n')

            # now, ids = dict of (uuid: (pid, instance-name)) elements
            for row in tabular:
                col = row.split()
                ids[col[2]] = (int(col[0]), col[1])

        except:
            # Warning! Fails silently...
            pass

        finally:
            return ids


class Inst_UPTIME(PeriodicInstMeterTask):
    def meter(self):
        """
        Returns a list of (UUID, timestamp, uptime [in seconds]) tuples, one
        for each instance running on a specific host.
        """
        uptimes = []

        try:
            # dict of (uuid: (pid, instance-name)) elements
            inst_ids = self._get_inst_ids()
            # list of (uuid, timestamp, uptime) tuples
            uptimes = [(uuid,
                        datetime.now(),
                        time.time() - process.create_time)
                       for (uuid, process) \
                           in [(k, psutil.Process(v[0])) \
                               for k, v in inst_ids.iteritems()]]

        except:
            # Warning! Fails silently...
            logger.exception('Inst_UPTIME: '
                             'Connection to hypervisor failed; reset.')
            self.conn = libvirt.openReadOnly(_LIBVIRT_SOCKET_URL)

        finally:
            return uptimes


class Inst_CPU_Time(PeriodicInstMeterTask):

    def __init__(self, callback, period):
        super(Inst_CPU_Time, self).__init__(callback, period)
        self.util_map = {}

    def meter(self):
        """
        Returns a list of (UUID, timestamp, cpu-time, cpu-time-ratio,
        cpu-percent) tuples, one for each instance running on a specific host.
        """
        inst_ids = None
        cpu_utils = []

        #@[fbahr] - TODO:
        #  - What about /proc/<pid>/stat?
        # ...
        try:
            domains = dict((self.conn.lookupByID(domain_id), None)
                           for domain_id in self.conn.listDomainsID())

            for domain in domains:
                uuid = domain.UUIDString()
                infos = domain.info()
                # ^ [0] state: one of the state values (virDomainState)
                #   [1] maxMemory: the maximum memory used by the domain
                #   [2] memory: the current amount of memory used by the domain
                #   [3] nbVirtCPU: the number of virtual CPU
                #   [4] cpuTime: the time used by the domain in nanoseconds
                num_vcpus, cpu_time = infos[3], infos[4]

                prev_cpu_util = self.util_map.get(uuid)

                # register new instance (if/when required: i.e., inst_ids
                # is None [_get_inst_ids hasn't been called in previous
                # iterations] *and* prev_cpu_util is None) ...
                # ^ When prev_cpu_util is None, but inst_ids isn't,
                #   _get_inst_ids has already neen called - and inst_ids
                #   provides all informations needed for subsequent
                #   execution(s).
                if not(prev_cpu_util or inst_ids):
                    inst_ids = self._get_inst_ids(pids=True)

                if not prev_cpu_util:
                    process = psutil.Process(inst_ids[uuid][0])
                    process.get_cpu_percent()  # tick 0 [not to be removed!,
                                               #         unless you really know
                                               #         what you're doing]
                else:
                    process = prev_cpu_util[2]

                self.util_map[uuid] = (datetime.now(), cpu_time, process)

                cpu_util = 0.0
                if prev_cpu_util:
                    prev_timestamp, prev_cpu_time, _ = prev_cpu_util

                    elapsed_real_time = (self.util_map[uuid][0] - prev_timestamp) \
                                            .total_seconds() \
                                            * (10 ** 9)
                    cores_fraction = 100.0 / num_vcpus  # in percent

                    #@[fbahr]: Warning: Account for cpu_time being reset when
                    #          the instance is restarted
                    cpu_time_used = cpu_time - (prev_cpu_time \
                                                if prev_cpu_time <= cpu_time \
                                                else 0)

                    cpu_util = cores_fraction * cpu_time_used / elapsed_real_time

                cpu_utils.append((uuid,
                                  datetime.now(),
                                  cpu_time,
                                  cpu_util,
                                  process.get_cpu_percent()))

            # unregister instances after shutdown (only checked when
            # _get_inst_ids has been called - i.e., "lazy evaluation")
            if inst_ids:
                shutdown = [_uuid for _uuid in self.util_map \
                            if _uuid not in inst_ids]
                for _uuid in shutdown:
                    del self.util_map[_uuid]

        except:
            # Warning! Fails silently...
            logger.exception('Inst_CPU_Time: '
                             'Connection to hypervisor failed; reset.')
            self.conn = libvirt.openReadOnly(_LIBVIRT_SOCKET_URL)

        finally:
            return cpu_utils


class Inst_PHYMEM_Usage(PeriodicInstMeterTask):
    #@[fbahr]: Join with Inst_VIRMEM_Usage?

    def __init__(self, callback, period):
        super(Inst_PHYMEM_Usage, self).__init__(callback, period)
        # self.psutil_vmem = psutil.virtual_memory()

    def meter(self):
        """
        Returns a list of (UUID, timestamp, phymem-attr) tuples, one for each
        instance running on a specific host.
        """
        phymem = []

        try:
            # dict of (uuid: (pid, instance-name)) elements
            inst_ids = self._get_inst_ids()
            # list of (uuid, timestamp, phymem [in bytes], phymem usage [in
            # pct of total]) tuples
            phymem = [(uuid,
                       datetime.now(),
                       process.get_memory_info().rss,
                       process.get_memory_percent())
                       # ^= float(process.get_memory_info().rss)
                       #    / self.psutil_vmem.total * 100
                      for (uuid, process) \
                          in [(k, psutil.Process(v[0])) \
                              for k, v in inst_ids.iteritems()]]

        except:
            # Warning! Fails silently...
            logger.exception('Inst_PHYMEM_Usage: '
                             'Connection to hypervisor failed; reset.')
            self.conn = libvirt.openReadOnly(_LIBVIRT_SOCKET_URL)

        finally:
            return phymem


class Inst_VIRMEM_Usage(PeriodicInstMeterTask):
    #@[fbahr]: Join with Inst_PHYMEM_Usage?

    def __init__(self, callback, period):
        super(Inst_VIRMEM_Usage, self).__init__(callback, period)
        self.psutil_smem = psutil.swap_memory()

    def meter(self):
        """
        Returns a list of (UUID, timestamp, virmem-attr) tuples, one for each
        instance running on a specific host.
        """
        virmem = []

        try:
            # dict of (uuid: (pid, instance-name)) elements
            inst_ids = self._get_inst_ids()
            # list of (uuid, timestamp, virmem [in bytes], virmem usage [in
            # pct of total]) tuples
            virmem = [(uuid,
                       datetime.now(),
                       mem_info.vms,
                       float(mem_info.vms) / self.psutil_smem.total * 100)
                      for (uuid, mem_info) \
                          in [(k, psutil.Process(v[0]).get_memory_info()) \
                              for k, v in inst_ids.iteritems()]]

        except:
            # Warning! Fails silently...
            logger.exception('Inst_VIRMEM_Usage: '
                             'Connection to hypervisor failed; reset.')
            self.conn = libvirt.openReadOnly(_LIBVIRT_SOCKET_URL)

        finally:
            return virmem


class Inst_NETWORK_IO(PeriodicInstMeterTask):

    def meter(self):
        """
        Returns a list of (UUID, timestamp, <network I/O>) tuples for all,
        one for each instance running on a specific host.
        """
        inst_net_ios = []

        try:
            domains = [self.conn.lookupByID(dom_id) \
                       for dom_id in self.conn.listDomainsID()]

            dom_descr = dict((dom, (dom.UUIDString(), dom.XMLDesc(0))) \
                              for dom in domains)

            for dom, descr in dom_descr.iteritems():
                #@[fbahr] - TODO: Exception handling?

                # tree = ETree.fromstring(descr[1])
                # vnets = []
                # for iface in tree.findall('devices/interface'):
                #     vnet = {}
                #     vnet['name'] = iface.find('target').get('dev')  # e.g. vnet1
                #     vnet['mac'] = iface.find('mac').get('address')  # ...
                #     vnet['fref'] = iface.find('filterref').get('filter')  # e.g. nova-instance-instance-00000028-fa163e4433d9
                #     for param in interface.findall('filterref/parameter'):
                #         vnet[param.get('name').lower()] = param.get('value')  # e.g. dhcpserver=192.168.4.33, ip=192.168.4.39
                #     vnets.append(vnet)

                vnets = filter(bool, \
                        # ^ prevents NoneType elements from being added to 'vnets'
                               [target.get('dev') for target in \
                                  ETree.fromstring(descr[1]). \
                                        findall('devices/interface/target')])

                iface_stats = [[iface_stat[0], iface_stat[1],  # r_bytes, r_packets
                                iface_stat[4], iface_stat[5]]  # w_bytes, w_packets
                                for iface_stat \
                                    in [dom.interfaceStats(vnet) \
                                        for vnet in vnets]]

                s = [sum(stat) for stat in zip(*iface_stats)]

                inst_net_ios.append((descr[0],  # uuid
                                     datetime.now(),
                                     s[0],      # r_bytes
                                     s[1],      # r_packets
                                     s[2],      # w_bytes
                                     s[3]))     # w_packets

        except:
            # Warning! Fails silently...
            logger.exception('Inst_NETWORK_IO: '
                             'Connection to hypervisor failed; reset.')
            self.conn = libvirt.openReadOnly(_LIBVIRT_SOCKET_URL)

        finally:
            return inst_net_ios


class Inst_DISK_IO(PeriodicInstMeterTask):
    #@[fbahr]: This meter is supposed to track "block storage" operations;
    #          ...what about: cinder (block storage) and swift (object storage)
    #          operations?

    def meter(self):
        """
        Returns a list of (UUID, timestamp, read_requests, bytes_read,
        write_requests, bytes_written) tuples, one for each instance
        running on a specific host.
        """
        inst_disk_ios = []

        #@[fbahr] Alternative implementation:
        #         psutil.Process(pid).get_io_counters().[read|write]_bytes
        try:
            domains = [self.conn.lookupByID(dom_id) \
                       for dom_id in self.conn.listDomainsID()]

            dom_descr = dict((dom, (dom.UUIDString(), dom.XMLDesc(0))) \
                             for dom in domains)

            for dom, descr in dom_descr.iteritems():
                #@[fbahr] - TODO: Exception handling?
                devices = filter(bool, \
                          # ^ prevents NoneType elements from being added to 'devices'
                                 [target.get('dev') for target in \
                                  ETree.fromstring(descr[1]). \
                                        findall('devices/disk/target')])

                block_stats = [dom.blockStats(dev) for dev in devices]

                s = [sum(stat) for stat in zip(*block_stats)]

                inst_disk_ios.append((descr[0],  # uuid
                                      datetime.now(),
                                      s[0],      # r_requests
                                      s[1],      # r_bytes
                                      s[2],      # w_requests
                                      s[3]))     # w_bytes
                #                     s[4]))     # errors

        except:
            # Warning! Fails silently...
            logger.exception('Inst_DISK_IO: '
                             'Connection to hypervisor failed; reset.')
            self.conn = libvirt.openReadOnly(_LIBVIRT_SOCKET_URL)

        finally:
            return inst_disk_ios

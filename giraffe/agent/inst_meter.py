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

Compute (Nova)
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


Network (Quantum) [NOT IMPLEMENTED]
------------------------  ----------  -------  -------- -----------------------
Name                      Type        Volume   Resource  Note
------------------------  ----------  -------  -------- -----------------------
network                   Gauge             1  netw ID   Duration of network
network.create            Delta       request  netw ID   Creation requests for this network
network.update            Delta       request  netw ID   Update requests for this network
subnet                    Gauge             1  subnt ID  Duration of subnet
subnet.create             Delta       request  subnt ID  Creation requests for this subnet
subnet.update             Delta       request  subnt ID  Update requests for this subnet
port                      Gauge             1  port ID   Duration of port
port.create               Delta       request  port ID   Creation requests for this port
port.update               Delta       request  port ID   Update requests for this port
router                    Gauge             1  rtr ID    Duration of router
router.create             Delta       request  rtr ID    Creation requests for this router
router.update             Delta       request  rtr ID    Update requests for this router
ip.floating               Gauge             1  ip ID     Duration of floating ip
ip.floating.create        Delta             1  ip ID     Creation requests for this floating ip
ip.floating.update        Delta             1  ip ID     Update requests for this floating ip
------------------------  ----------  -------  -------- -----------------------


Image (Glance) [NOT IMPLEMENTED]
------------------------  ----------  -------  -------- -----------------------
Name                      Type        Volume   Resource  Note
------------------------  ----------  -------  -------- -----------------------
image                     Gauge             1  image ID  Image polling -> it (still) exists
image.size                Gauge         bytes  image ID  Uploaded image size
image.update              Delta          reqs  image ID  Number of update on the image
image.upload              Delta          reqs  image ID  Number of upload of the image
image.delete              Delta          reqs  image ID  Number of delete on the image
image.download            Delta         bytes  image ID  Image is downloaded
image.serve               Delta         bytes  image ID  Image is served out
------------------------  ----------  -------  -------- -----------------------


Volume (Cinder) [NOT IMPLEMENTED]
------------------------  ----------  -------  -------- -------------------
Name                      Type        Volume   Resource  Note
------------------------  ----------  -------  -------- -------------------
volume                    Gauge             1  vol ID    Duration of volune
volume.size               Gauge            GB  vol ID    Size of volume
------------------------  ----------  -------  -------- -------------------


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
logger = logging.getLogger("agent.inst_meters")
# logger.setLevel(logging.DEBUG)
# formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
# fh = logging.FileHandler("agent.log")
# fh.setFormatter(formatter)
# logger.addHandler(fh)


def get_inst_ids(connection, pids=True):
    """
    Returns a dict of (uuid: (pid, instance-name)) elements for instances
    running on a certain host.
    """
    #@[fbahr] To do: Lookups for UUIDs and PIDs are considered "harmful",
    #         so: figure out a way to perform these only whenever
    #         really neccessary
    ids = {}

    try:
        # dict of (uuid: None) elements, in short: instances running on a host
        for domain_id in connection.listDomainsID():
            ids[connection.lookupByID(domain_id).UUIDString()] = None

        # ^ alt. implementation
        # ---------------------
        # ids = dict((uuid, None)
        #            for uuid in [connection.lookupByID(domain_id).UUIDString()
        #                         for domain_id in connection.listDomainsID()])

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

        # ^ alt. implementation
        # ---------------------
        # [ids[col[2]] = (col[0], col[1])
        #                for col in [row.split() for row in tabular]]

    except:
        # Warning! Fails silently...
        pass

    finally:
        return ids


class PeriodicInstMeterTask(PeriodicMeterTask):

    def __init__(self, callback, period):
        super(PeriodicInstMeterTask, self).__init__(callback, period)

        self.conn = libvirt.openReadOnly(_LIBVIRT_SOCKET_URL)
        if not self.conn:
            logger.exception('PeriodicInstMeterTask: '
                             'Failed to open connection to hypervisor.')
            sys.exit(1)

        #@[fbahr]: maybe it's a good idea to move this - i.e., gathering
        #          user and tenant informations for an instance via the
        #          nova-client - to the service (collector)
        _credentials = dict(username=_config.get('agent', 'user'),
                            password=_config.get('agent', 'pass'),
                            tenant_id=_config.get('agent', 'tenant_id'),
                            tenant_name=_config.get('agent', 'tenant_name'),
                            auth_url=_config.get('auth', 'auth_url'),
                            insecure=True)

        _credentials['api_key'] = AuthProxy.get_token(**_credentials)

        self.nova_client = NovaClient(username=_credentials['username'],
                                      api_key=_credentials['api_key'],
                                      project_id=_credentials['tenant_id'],
                                      auth_url=_credentials['auth_url'],
                                      insecure=True)
        self.nova_client.client.auth_token = _credentials['api_key']
        # self.nova_client.client.authenticate()
        # ^ raises exceptions.Unauthorized - TODO: fix auth


class Inst_UPTIME(PeriodicInstMeterTask):
    def meter(self):
        """
        Returns a list of (UUID, timestamp, uptime [in seconds]) tuples, one
        for each instance running on a specific host.
        """
        uptimes = []

        try:
            # dict of (uuid: (pid, instance-name)) elements
            inst_ids = get_inst_ids(self.conn)
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


class Inst_CPU(PeriodicInstMeterTask):

    def __init__(self, callback, period):
        super(Inst_CPU, self).__init__(callback, period)
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
                # is None [get_inst_ids hasn't been called in previous
                # iterations] *and* prev_cpu_util is None) ...
                # ^ When prev_cpu_util is None, but inst_ids isn't,
                #   get_inst_ids has already neen called - and inst_ids
                #   provides all informations needed for subsequent
                #   execution(s).
                if not(prev_cpu_util or inst_ids):
                    inst_ids = get_inst_ids(self.conn, pids=True)

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
            # get_inst_ids has been called - i.e., "lazy evaluation")
            if inst_ids:
                shutdown = [_uuid for _uuid in self.util_map \
                            if _uuid not in inst_ids]
                for _uuid in shutdown:
                    del self.util_map[_uuid]

        except:
            # Warning! Fails silently...
            logger.exception('Inst_CPU: '
                             'Connection to hypervisor failed; reset.')
            self.conn = libvirt.openReadOnly(_LIBVIRT_SOCKET_URL)

        finally:
            return cpu_utils


class Inst_PHYMEM(PeriodicInstMeterTask):
    #@[fbahr]: Join with Inst_VIRMEM?

    def __init__(self, callback, period):
        super(Inst_PHYMEM, self).__init__(callback, period)
        # self.psutil_vmem = psutil.virtual_memory()

    def meter(self):
        """
        Returns a list of (UUID, timestamp, phymem-attr) tuples, one for each
        instance running on a specific host.
        """
        phymem = []

        try:
            # dict of (uuid: (pid, instance-name)) elements
            inst_ids = get_inst_ids(self.conn)
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
            logger.exception('Inst_PHYMEM: '
                             'Connection to hypervisor failed; reset.')
            self.conn = libvirt.openReadOnly(_LIBVIRT_SOCKET_URL)

        finally:
            return phymem


class Inst_VIRMEM(PeriodicInstMeterTask):
    #@[fbahr]: Join with Inst_PHYMEM?

    def __init__(self, callback, period):
        super(Inst_VIRMEM, self).__init__(callback, period)
        self.psutil_smem = psutil.swap_memory()

    def meter(self):
        """
        Returns a list of (UUID, timestamp, virmem-attr) tuples, one for each
        instance running on a specific host.
        """
        virmem = []

        try:
            # dict of (uuid: (pid, instance-name)) elements
            inst_ids = get_inst_ids(self.conn)
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
            logger.exception('Inst_VIRMEM: '
                             'Connection to hypervisor failed; reset.')
            self.conn = libvirt.openReadOnly(_LIBVIRT_SOCKET_URL)

        finally:
            return virmem


class NetPollster(LibVirtPollster):
    pass
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
                              for dom in domain)

            for dom, descr in dom_descr.iteritems():
                #@[fbahr] - TODO: Exception handling?
                tree = Etree.fromstring(decr[1])
                vnics = []
                for interace in tree.findall('devices/interface'):
                    vnic = {}
                    vnic['name'] = interface.find('target').get('dev')
                    if vnic['name'].startswith('lo'):
                        continue
                    # vnic['mac'] = interface.find('mac').get('address')
                    # vnic['fref'] = interface.find('filterref').get('filter')
                    # for param in interface.findall('filterref/parameter'):
                    #     vnic[param.get('name').lower()] = param.get('value')
                    vnics.append(vnic)

                timestamp = datetime.now()
                for vnic in vnics:
                    rx_bytes, rx_packets, _, _,
                    tx_bytes, tx_packets, _, _ \
                        = domain.interfaceStats(vnic['name'])
                
                

                yield self.make_vnic_counter(instance,
                                             name='network.outgoing.bytes',
                                             type=counter.TYPE_CUMULATIVE,
                                             volume=tx_bytes,
                                             vnic_data=vnic,
                                             )
                yield self.make_vnic_counter(instance,
                                             name='network.incoming.packets',
                                             type=counter.TYPE_CUMULATIVE,
                                             volume=rx_packets,
                                             vnic_data=vnic,
                                             )




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

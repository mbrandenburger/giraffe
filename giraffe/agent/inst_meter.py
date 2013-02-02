__author__ = 'marcus, fbahr'

"""
In giraffe (as known from ceilometer), three type of meters are defined:

----------  -------------------------------------------------------------------
Type        Definition
----------  -------------------------------------------------------------------
Cumulative  Increasing over time (instance hours)
Gauge       Discrete items (floating IPs, image uploads) 
            and fluctuating values (disk I/O)
Delta       Changing over time (bandwidth)
----------  -------------------------------------------------------------------


-------------------------------------------------------------------------------
Implemented meters
-------------------------------------------------------------------------------
+ [Inst_UUIDs]
- Inst_CPU_Usage    (raises NotImplementedError)
+ Inst_PHYMEM_Usage
+ Inst_VIRMEM_Usage
+ Inst_UPTIME
- Inst_NETWORK_IO   (raises NotImplementedError)
+ Inst_DISK_IO

? Inst_ ...         [meter for cinder (block storage) operations]
? Inst_ ...         [meter for swift (object storage) operations]
?       ...



==============






Here are the meter types by components that are currently implemented:

Compute (Nova)
==============

========================  ==========  =======  ========  =======================================================
Name                      Type        Volume   Resource  Note
========================  ==========  =======  ========  =======================================================
instance                  Gauge             1  inst ID   Duration of instance
instance:<type>           Gauge             1  inst ID   Duration of instance <type> (openstack types)
memory                    Gauge            MB  inst ID   Volume of RAM in MB
cpu                       Cumulative       ns  inst ID   CPU time used
vcpus                     Gauge          vcpu  inst ID   Number of VCPUs
disk.root.size            Gauge            GB  inst ID   Size of root disk in GB
disk.ephemeral.size       Gauge            GB  inst ID   Size of ephemeral disk in GB


inst.disk.io.requests     Cumulative  request  inst ID   Number of disk io requests
inst.disk.io.bytes             Cumulative    bytes  inst ID   Volume of disk io in bytes

network.incoming.bytes    Cumulative    bytes  iface ID  number of incoming bytes on the network
network.outgoing.bytes    Cumulative    bytes  iface ID  number of outgoing bytes on the network
network.incoming.packets  Cumulative  packets  iface ID  number of incoming packets
network.outgoing.packets  Cumulative  packets  iface ID  number of outgoing packets
========================  ==========  =======  ========  =======================================================

Network (Quantum)
=================

========================  ==========  =======  ========  =======================================================
Name                      Type        Volume   Resource  Note
========================  ==========  =======  ========  =======================================================
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
========================  ==========  =======  ========  =======================================================

Image (Glance)
==============

========================  ==========  =======  ========  =======================================================
Name                      Type        Volume   Resource  Note
========================  ==========  =======  ========  =======================================================
image                     Gauge             1  image ID  Image polling -> it (still) exists
image.size                Gauge         bytes  image ID  Uploaded image size
image.update              Delta          reqs  image ID  Number of update on the image
image.upload              Delta          reqs  image ID  Number of upload of the image
image.delete              Delta          reqs  image ID  Number of delete on the image
image.download            Delta         bytes  image ID  Image is downloaded
image.serve               Delta         bytes  image ID  Image is served out
========================  ==========  =======  ========  =======================================================

Volume (Cinder)
===============

========================  ==========  =======  ========  =======================================================
Name                      Type        Volume   Resource  Note
========================  ==========  =======  ========  =======================================================
volume                    Gauge             1  vol ID    Duration of volune
volume.size               Gauge            GB  vol ID    Size of volume
========================  ==========  =======  ========  =======================================================

Naming convention
=================
If you plan on adding meters, please follow the convention bellow:

1. Always use '.' as separator and go from least to most discriminent word.
   For example, do not use ephemeral_disk_size but disk.ephemeral.size

2. When a part of the name is a variable, it should always be at the end and start with a ':'.
   For example do not use <type>.image but image:<type>, where type is your variable name.



-------------------------------------------------------------------------------
3rd-party modules/dependencies
-------------------------------------------------------------------------------
psutil
libvirt
"""

import sys
import time
from datetime import datetime
import subprocess
import logging
from xml.etree import ElementTree as ETree

import psutil

# try:
#     from nova.virt import driver
# except ImportError:
import libvirt

from giraffe.common.task import PeriodicMeterTask


logger = logging.getLogger("agent.inst_meters")
logger.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
ch = logging.StreamHandler()
ch.setFormatter(formatter)
logger.addHandler(ch)


def get_inst_ids(connection, pids=True):
    """
    Returns a dict of (uuid: (pid, instance-name)) elements for instances
    running on a certain host
    """
    #@[fbahr] To do: Lookups for UUIDs and PIDs are considered harmful,
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

    return ids


class PeriodicInstMeterTask(PeriodicMeterTask):
    def __init__(self, callback, period):
        super(PeriodicInstMeterTask, self).__init__(callback, period)

        self.conn = libvirt.openReadOnly(None)
        if not self.conn:
            logger.exception('Failed to open connection to hypervisor.')
            sys.exit(1)


class Inst_UUIDs(PeriodicInstMeterTask):
    #@[fbahr]: Actually, this is rather a host meter... for the time being,
    #          left as an instance metering task [since: subclassing 
    #          PeriodicInstMeterTask]
    #          Hence, rather than a list of UUIDs, a record (UNAME,
    #          timestamp,  list of UUIDs) should be returned

    def meter(self):
        """
        Returns a list of instance UUIDs
        """
        uuids = []

        try:
            uuids = get_inst_ids(self.conn, pids=False).keys()
        except:
            # Warning! Fails silently...
            logger.exception('Connection to hypervisor failed; reset.')
            self.conn = libvirt.openReadOnly(None)

        return uuids


class Inst_CPU_Usage(PeriodicInstMeterTask):
    #@[fbahr]: Leverage/reuse get_inst_ids()?

    def __init__(self, callback, period):
        super(Inst_CPU_Usage, self).__init__(callback, period)
        self.utilization_map = {}

    def meter(self):
        """
        Returns a list of CPU utilization for every instance running on a
        specific host
        """
        raise NotImplementedError()

        try:
            #@[fbahr]: 
            #  - What about /proc/<pid>/stat?
            #  - psutil.process.get_memory_percent() and %CPU as reported by
            #    virt-top differ significantly

            domains = [self.conn.lookupByID(domain_id)
                       for domain_id in self.conn.listDomainsID()]

            for domain in domains:
                uuid = domain.UUIDString()

                prev_cpu_times = self.utilization_map.get(uuid)
            #-  self.utilization_map[uuid] = (cpu_info['cpu_time'],
            #-                                time.time())

            #   pid = get_instance_pid(uuid)
            #   process = psutil.Process(pid)
            #   load_avg = process.get_cpu_percent(interval=1.0)

            #-  cpu_info = self.conn.get_info({'name': domain.name()})
            #-  num_cpus, cpu_time = cpu_info['num_cpu'], cpu_info['cpu_time']
                infos = domain.info()
                num_cpus, cpu_time = infos[3], infos[4]

                self.utilization_map[uuid] = (cpu_time, datetime.now())

                cpu_util = 0.0
                if prev_cpu_times:
                    prev_cpu = prev_cpu_times[0]
                    prev_timestamp = prev_cpu_times[1]

                    delta = self.utilization_map[uuid][1] - prev_timestamp
                    elapsed = (delta.seconds * (10**6) + delta.microseconds) * 1000

                    cores_fraction = 1.0 / num_cpus

                # account for cpu_time being reset when the instance is restarted
            time_used = (cpu_time - prev_cpu
                         if prev_cpu <= cpu_time else
                         cpu_time)
            cpu_util = 100 * cores_fraction * time_used / elapsed
            return cpu_util
        except Exception as e:
            logger.exception("%s" % e)


class Inst_PHYMEM_Usage(PeriodicInstMeterTask):
    #@[fbahr]: Join with Inst_VIRMEM_Usage?

    def __init__(self, callback, period):
        super(Inst_PHYMEM_Usage, self).__init__(callback, period)
        # self.psutil_vmem = psutil.virtual_memory()

    def meter(self):
        """
        Returns a list of (UUID, timestamp, phymem-attr) tuples, one for each
        instance running on a specific host
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
            logger.exception('Connection to hypervisor failed; reset.')
            self.conn = libvirt.openReadOnly(None)

        return phymem


class Inst_VIRMEM_Usage(PeriodicInstMeterTask):
    #@[fbahr]: Join with Inst_PHYMEM_Usage?

    def __init__(self, callback, period):
        super(Inst_VIRMEM_Usage, self).__init__(callback, period)
        self.psutil_smem = psutil.swap_memory()

    def meter(self):
        """
        Returns a list of (UUID, timestamp, virmem-attr) tuples, one for each
        instance running on a specific host
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
            logger.exception('Connection to hypervisor failed; reset.')
            self.conn = libvirt.openReadOnly(None)

        return virmem


class Inst_UPTIME(PeriodicInstMeterTask):
    def meter(self):
        """
        Returns a list of (UUID, timestamp, uptime [in seconds]) tuples, one
        for each instance running on a specific host
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
            logger.exception('Connection to hypervisor failed; reset.')
            self.conn = libvirt.openReadOnly(None)

        return uptimes


class Inst_NETWORK_IO(PeriodicInstMeterTask):
    def meter(self):
        """
        Returns a list of IDs and corresponding network I/O (in bytes) for all
        instances running on a specific host
        """
        return NotImplementedError()


class Inst_DISK_IO(PeriodicInstMeterTask):
    #@[fbahr]: This meter is supposed to track "block storage" operations;
    #          ...what about: cinder (block storage) and swift (object storage)
    #          operations?

    def meter(self):
        """
        Returns a list of (UUID, timestamp, read_rquests, bytes_read, 
        write_requests, bytes_written) tuples, one for each instance 
        running on a specific host
        """
        inst_ios = []

        try:
            # # dict of (uuid: (pid, instance-name)) elements
            # inst_ids = get_inst_ids(self.conn)
            # # list of (uuid, uptime) tuples
            # inst_ios = [(uuid,
            #             datetime.now(),
            #             io_counter.read_bytes,
            #             io_counter.write_bytes)
            #            for (uuid, io_counter) \
            #                in [(k, psutil.Process(v[0]).get_io_counters()) \
            #                    for k, v in inst_ids.iteritems()]]

            # ^ alternative implementation ------------------------------------
            domains = [self.conn.lookupByID(dom_id) \
                       for dom_id in self.conn.listDomainsID()]

            dom_descr = dict((dom, (dom.UUIDString(), dom.XMLDesc(0))) \
                             for dom in domains)

            for dom, descr in dom_descr.iteritems():
                devices = filter(bool, \
                                 [target.get('dev') for target in \
                                  ETree.fromstring(descr[1]). \
                                        findall('devices/disk/target')])

                block_stats = [dom.blockStats(dev) for dev in devices]

                s = [sum(stat) for stat in zip(*block_stats)]

                inst_ios.append((descr[0],  # uuid
                                 datetime.now(),
                                 s[0],      # r_requests
                                 s[1],      # r_bytes
                                 s[2],      # w_requests
                                 s[3]))     # w_bytes
                #                s[4]))     # errors

        except:
            # Warning! Fails silently...
            logger.exception('Connection to hypervisor failed; reset.')
            self.conn = libvirt.openReadOnly(None)

        return inst_ios

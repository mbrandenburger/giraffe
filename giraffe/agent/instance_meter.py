__author__ = 'marcus, fbahr'

"""
3rd-party modules/dependencies: psutil, libvirt
"""

import sys
import subprocess
import logging
import psutil

# try:
#     from nova.virt import driver
# except ImportError:
import libvirt

import time
from datetime import datetime, timedelta
from giraffe.common.task import PeriodicMeterTask


logger = logging.getLogger("service.collector.instance_meters")


def get_instance_ids(connection, pids=True):
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


class PeriodicInstanceMeterTask(PeriodicMeterTask):
    def __init__(self):
        self.conn = libvirt.openReadOnly(None)
        if not self.conn:
            logger.exception('Failed to open connection to hypervisor.')
            sys.exit(1)


class Instance_UUIDs(PeriodicInstanceMeterTask):
    #@[fbahr]: Actually, this is rather a host meter... for the time being,
    #          left as an instance metering task [since: subclassing 
    #          PeriodicInstanceMeterTask]
    #          Hence, rather than a list of UUIDs, a record (UNAME,
    #          timestamp,  list of UUIDs) should be returned
    def meter(self):
        """
        Returns a list of instance UUIDs
        """
        uuids = []

        try:
            uuids = get_instance_ids(self.conn, pids=False).keys()
        except:
            # Warning! Fails silently...
            logger.exception('Connection to hypervisor failed; reset.')
            self.conn = libvirt.openReadOnly(None)

        return uuids


class Instance_CPU_utilizations(PeriodicInstanceMeterTask):
    def __init__(self):
        super(Instance_CPU_utilizations, self).__init__()
        self.utilization_map = {}

    def meter(self):
        """
        Returns a list of CPU utilization for every instance running on a
        specific host
        """
        domains = [self.conn.lookupByID(domain_id)
                   for domain_id in self.conn.listDomainsID()]

        for domain in domains:
            uuid = domain.UUIDString()

            # pid = get_instance_pid(uuid)
            # process = psutil.Process(pid)
            # load_avg = process.get_cpu_percent(interval=1.0)

            infos = domain.info()
            cpu_time = infos[2]
            num_cpus = infos[3]
            #- cpu_info = self.conn.get_info({'name': domain.name()})
            #- ^ @[fbahr]: required for cpu_info['cpu_time'], cpu_info['num_cpu'] 

            prev_cpu_times = self.utilization_map.get(uuid)
            #- self.utilization_map[uuid] = (cpu_info['cpu_time'],
            #-                               time.time())
            self.utilization_map[uuid] = (cpu_time,
                                          time.time())

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


class Instance_PHYMEM_Usages(PeriodicInstanceMeterTask):
    #@[fbahr]: Join with Instance_VIRTMEM_Usages?

    def meter(self):
        """ 
        Returns a list of current physical memory usage for every instance 
        running on a specific host
        """
        raise NotImplementedError()


class Instance_VIRTMEM_Usages(PeriodicInstanceMeterTask):
    #@[fbahr]: Join with Instance_PHYMEM_Usages?

    def meter(self):
        """
        Returns a list of (UUID, timestamp, virtmem) tuples, one for each 
        instance running on a specific host
        """
        virtmem = []

        try:
            # dict of (uuid: (pid, instance-name)) elements
            inst_ids = get_instance_ids(self.conn)
            # list of (uuid, uptime) tuples
            virtmem = [(uuid,
                        time.time(),
                        mem_info.vms)
                        for (uuid, mem_info) \
                            in [(k, psutil.Process(v[0]).get_memory_info()) \
                                for k, v in inst_ids.iteritems()]]
        except:
            # Warning! Fails silently...
            logger.exception('Connection to hypervisor failed; reset.')
            self.conn = libvirt.openReadOnly(None)

        # return virtmem

        raise NotImplementedError()


class Instance_UPTIMEs(PeriodicInstanceMeterTask):
    def meter(self):
        """
        Returns a list of (UUID, timestamp, uptime [in seconds]) tuples, one
        for each instance running on a specific host
        """
        uptimes = []

        try:
            # dict of (uuid: (pid, instance-name)) elements
            inst_ids = get_instance_ids(self.conn)
            # list of (uuid, uptime) tuples
            uptimes = [(uuid,
                        time.time(), 
                        float('%1.2f'
                              % ((time.time() - process.create_time) * 1000)))
                       for (uuid, process) \
                           in [(k, psutil.Process(v[0])) \
                               for k, v in inst_ids.iteritems()]]

            # ^ alt. implementation
            # ---------------------
            # uuids = [self.conn.lookupByID(domain_id).UUIDString() 
            #          for domain_id in self.conn.listDomainsID()]
            #
            # for domain_id in self.conn.listDomainsID():
            #     domain = self.conn.lookupByID(domain_id)
            #     uuid = domain.UUIDString()
            #
            #     pid = get_instance_pid(uuid)
            #     process = psutil.Process(pid)
            #
            #     uptimes.append([
            #         uuid,
            #         float('%1.2f' % ((time.time() - process.create_time) * 1000))
            #         ])
        except:
            # Warning! Fails silently...
            logger.exception('Connection to hypervisor failed; reset.')
            self.conn = libvirt.openReadOnly(None)

        return uptimes


class Instance_NETWORK_IOs(PeriodicInstanceMeterTask):
    def meter(self):
        """
        Returns a list of IDs and corresponding network I/O (in bytes) for all
        instances running on a specific host
        """
        return NotImplementedError()


class Instance_DISK_IOs(PeriodicInstanceMeterTask):
    #@[fbahr]: Actually, this should rather refer to Object (swift) and/or
    #          Block Storage (cinder) usage.

    def meter(self):
        """
        Returns a list of (UUID, timestamp, bytes_read, bytes_written) tuples,
        one for each instance running on a specific host
        """
        inst_ios = []

        try:
            # dict of (uuid: (pid, instance-name)) elements
            inst_ids = get_instance_ids(self.conn)
            # list of (uuid, uptime) tuples
            inst_ios = [(uuid,
                         time.time(),
                         io_counter.read_bytes,
                         io_counter.write_bytes)
                        for (uuid, io_counter) \
                            in [(k, psutil.Process(v[0]).get_io_counters()) \
                                for k, v in inst_ids.iteritems()]]
        except:
            # Warning! Fails silently...
            logger.exception('Connection to hypervisor failed; reset.')
            self.conn = libvirt.openReadOnly(None)

        # return inst_ios
        raise NotImplementedError()

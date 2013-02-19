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

Host
--------------------------------  -------------  ----------  ----------  ------
Name                              Type           Volume      Resource    Note
--------------------------------  -------------  ----------  ----------  ------
...
--------------------------------  -------------  ----------  ----------  ------


Naming convention
-----------------
If you plan on adding meters, please follow the convention bellow:

1. Always use '.' as separator and go from least to most discriminent word.
   For example, do not use ephemeral_disk_size but disk.ephemeral.size

2. When a part of the name is a variable, it should always be at the end and
   start with a ':'. For example do not use <type>.image but image:<type>,
   where type is your variable name.
"""


import os
import sys
from datetime import datetime
import libvirt
import psutil
from giraffe.common.task import PeriodicMeterTask

import logging
logger = logging.getLogger("agent.host_meters")


class PeriodicHostMeterTask(PeriodicMeterTask):

    def __init__(self, callback, period):
        super(PeriodicHostMeterTask, self).__init__(callback, period)
        pass


class Host_UNAME(PeriodicHostMeterTask):
    def meter(self):
        """
        Returns uname
        """
        return os.uname()


class Host_INST_Count(PeriodicHostMeterTask):

    def __init__(self, callback, period):
        super(Host_INST_Count, self).__init__(callback, period)
        self.conn = libvirt.openReadOnly('qemu:///system')
        if not self.conn:
            logger.exception('Failed to open connection to hypervisor.')
            sys.exit(1)

    def meter(self):
        """
        Returns a list of (UUID, timestamp, domain-state) tuples, one for each
        instance running on a specific host.
        """
        num_instances = -1
    #   uuids = []

        try:
            num_instances = self.conn.numOfDomains()
    #       domains = [self.conn.lookupByID(domain_id) \
    #                       for domain_id in self.conn.listDomainsID()]
    #       time = datetime.now()
    #
    #       uuids = [[d.UUIDString(), time, d.info()[0]] for d in domains]

        except:
            # Warning! Fails silently...
            logger.exception('Connection to hypervisor failed; reset.')
            self.conn = libvirt.openReadOnly('qemu:///system')

        finally:
            return num_instances
    #       return uuids


class Host_UPTIME(PeriodicHostMeterTask):

    def meter(self):
        """
        Returns uptime in seconds
        """
        uptime = 0.0
        try:
            with open('/proc/uptime', 'r') as f:
                uptime = float(f.readline().split()[0])
        finally:
            return uptime


class Host_CPU_Load(PeriodicHostMeterTask):

    def meter(self):
        """
        Returns current system load average
        """
        return os.getloadavg()


class Host_PHYMEM_Usage(PeriodicHostMeterTask):
    # @[fbahr]: Join with Host_VIRMEM_Usage?

    def meter(self):
        """
        Returns current physical memory usage
        """
        # psutil.phymem_usage() deprecated in psutil v0.6.0
        mem = psutil.virtual_memory()
        return [mem.total, mem.used, mem.free, mem.percent]
        # ^ return _nt_sysmeminfo(mem.total, mem.used, mem.free, mem.percent)
        #          -> usage(total=..L, used=1..L, free=..L, percent=x.y)


class Host_VIRMEM_Usage(PeriodicHostMeterTask):
    # @[fbahr]: Join with Host_PHYMEM_Usage?

    def meter(self):
        """
        Returns current virtual memory usage
        """
        # psutil.virtmem_usage() deprecated in psutil v0.6.0
        return psutil.swap_memory()
        #      -> swap(total=..L, used=..L, free=..L, percent=x.y, sin=.., sout=..)


class Host_DISK_IO(PeriodicHostMeterTask):

    def meter(self):
        """
        Returns current disk I/O in byte
        """
        raise NotImplementedError()


class Host_NETWORK_IO(PeriodicHostMeterTask):

    def meter(self):
        """
        Returns current network I/O in byte
        """
        return psutil.network_io_counters()

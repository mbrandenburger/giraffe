__author__ = 'mbrandenburger, fbahr'

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
# from datetime import datetime
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
    # https://wiki.openstack.org/wiki/NovaDatabaseSchema
    # ? .nova.compute_nodes. ..

    def meter(self):
        """
        Returns uname
        """
        return os.uname()


class Host_INST_Count(PeriodicHostMeterTask):
    # https://wiki.openstack.org/wiki/NovaDatabaseSchema
    # > .nova.compute_nodes.running_vms

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
    # https://wiki.openstack.org/wiki/NovaDatabaseSchema
    # ? .nova.compute_nodes. ..

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
    # https://wiki.openstack.org/wiki/NovaDatabaseSchema
    # ? .nova.compute_nodes. ..

    def meter(self):
        """
        Returns current system load average
        """
        return os.getloadavg()


class Host_MEMORY_Usage(PeriodicHostMeterTask):
    # https://wiki.openstack.org/wiki/NovaDatabaseSchema
    # ? .nova.compute_nodes. ..

    def meter(self):
        """
        Returns current physical and virtual memory usage
        """
        # Note:
        # - psutil.virtmem_usage(),
        # - psutil.phymem_usage()
        # have been deprecated in psutil v0.6.0
        #
        # From https://github.com/packages/psutil/blob/master/HISTORY:
        #
        # "system memory functions has been refactorized and rewritten and
        #  now provide a more detailed and consistent representation of
        #  the system memory."
        #
        # From http://code.google.com/p/psutil/wiki/Documentation:
        #
        # psutil.virtual_memory():
        #   Return statistics about system memory usage as a namedtuple
        #   including the following fields, expressed in bytes:
        #   - total: total *physical* memory available
        #   - available: the actual amount of available memory that can be
        #       given instantly to processes that request more memory in
        #       bytes; this is calculated by summing different memory values
        #       depending on the platform (e.g. free + buffers + cached on
        #       Linux) and it is supposed to be used to monitor actual memory
        #       usage in a cross platform fashion.
        #   - percent: the percentage usage calculated as
        #       (total - available) / total * 100
        #   - used: memory used, calculated differently depending on the
        #       platform and designed for informational purposes only.
        #   - free: memory not being used at all (zeroed) that is readily
        #       available; note that this doesn't reflect the actual memory
        #       available (use 'available' instead).
        #
        #   Example:
        #   > vmem(total=8374149120L, available=1247768576L, percent=85.1,
        #          used=8246628352L, free=127520768L, ...)
        #
        # psutil.swap_memory():
        #   Return system swap memory statistics as a namedtuple including
        #   the following attributes:
        #   - total: total swap memory in bytes
        #   - used: used swap memory in bytes
        #   - free: free swap memory in bytes
        #   - percent: the percentage usage
        #   - sin: no. of bytes the system has swapped in from disk (cumulative)
        #   - sout: no. of bytes the system has swapped out from disk (cumulative)
        #     ('sin' and 'sout' on Windows are meaningless and always set to 0.)
        #
        #   Example:
        #   > swap(total=2097147904L, used=886620160L, free=1210527744L,
        #          percent=42.3, sin=1050411008, sout=1906720768)

        # @[fbahr]: seriously, psutil.virtual_memory() to access physical
        #           memory stats!? [naming issue?]
        phy_mem = psutil.virtual_memory()
        # ^ from: _nt_sysmeminfo(mem.total, mem.used, mem.free, mem.percent)
        #         -> usage(total=..L, used=1..L, free=..L, percent=x.y)

        vir_mem = psutil.swap_memory()
        #         -> swap(total=..L, used=..L, free=..L, percent=x.y, sin=.., sout=..)

        return [phy_mem.total,      # 0
                phy_mem.available,  # 1
                phy_mem.used,       # 2
                phy_mem.percent,    # 3 - used to report phy_mem usage
                vir_mem.total,      # 4 - used to report vir_mem usage
                vir_mem.used,       # 5 - used to report vir_mem usage
                vir_mem.free,       # 6
                vir_mem.percent]    # 7


class Host_DISK_IO(PeriodicHostMeterTask):
    # https://wiki.openstack.org/wiki/NovaDatabaseSchema
    # ? .nova. ..

    def meter(self):
        """
        Returns current disk I/O in byte
        """
        raise NotImplementedError()


class Host_NETWORK_IO(PeriodicHostMeterTask):
    # https://wiki.openstack.org/wiki/NovaDatabaseSchema
    # ? .nova. ..

    def meter(self):
        """
        Returns current network I/O in byte
        """
        return psutil.network_io_counters()

__author__ = 'marcus'

import os
import psutil
from giraffe.common.task import PeriodicMeterTask


class Host_UNAME(PeriodicMeterTask):
    def meter(self):
        """
        Returns uname
        """
        return os.uname()


class Host_CPU_AVG(PeriodicMeterTask):
    def meter(self):
        """
        Returns current system load average
        """
        return os.getloadavg()


class Host_PHYMEM_Usage(PeriodicMeterTask):
    # @[fbahr]: Join with Host_VIRMEM_Usage?
    def meter(self):
        """
        Returns current physical memory usage
        """
        # psutil.phymem_usage() deprecated in psutil v0.6.0
        mem = psutil.virtual_memory()
        return [mem.total, mem.used, mem.free, mem.percent]
        # ^ return _nt_sysmeminfo(mem.total, mem.used, mem.free, mem.percent)
        #   -> usage(total=..L, used=1..L, free=..L, percent=x.y)


class Host_VIRMEM_Usage(PeriodicMeterTask):
    # @[fbahr]: Join with Host_PHYMEM_Usage?
    def meter(self):
        """
        Returns current virtual memory usage
        """
        # psutil.virtmem_usage() deprecated in psutil v0.6.0
        return psutil.swap_memory()
        # -> swap(total=..L, used=..L, free=..L, percent=x.y, sin=.., sout=..)


class Host_UPTIME(PeriodicMeterTask):
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


class Host_NETWORK_IO(PeriodicMeterTask):
    def meter(self):
        """
        Returns current network I/O in byte
        """
        return psutil.network_io_counters()


class Host_DISK_IO(PeriodicMeterTask):
    def meter(self):
        """
        Returns current disk I/O in byte
        """
        raise NotImplementedError()

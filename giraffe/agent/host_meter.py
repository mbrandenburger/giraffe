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
    def meter(self):
        """
        Returns current physical memory usage
        """
        # deprecated in psutil v0.6.0
        # return psutil.phymem_usage()
        # usage(total=25269719040L, used=11895799808L, free=13373919232L, percent=16.8)

        mem = psutil.virtual_memory()
        return [mem.total, mem.used, mem.free, mem.percent]
        # return _nt_sysmeminfo(mem.total, mem.used, mem.free, mem.percent)


class Host_VIRMEM_Usage(PeriodicMeterTask):
    def meter(self):
        """
        Returns current virtual memory usage
        """
        return psutil.virtmem_usage()


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

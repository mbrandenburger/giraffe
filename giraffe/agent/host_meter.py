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
        return psutil.phymem_usage()


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


import os
import psutil
from giraffe.common.task import PeriodicMeterTask


class Host_CPU_AVG(PeriodicMeterTask):
    def meter(self):
        avg = os.getloadavg()
        return avg


class Host_UNAME(PeriodicMeterTask):
    def meter(self):
        uname = os.uname()
        return uname


class Host_PHYMEM_Usage(PeriodicMeterTask):
    def meter(self):
        return psutil.phymem_usage()


class Host_VIRTMEM_Usage(PeriodicMeterTask):
    def meter(self):
        return psutil.virtmem_usage()

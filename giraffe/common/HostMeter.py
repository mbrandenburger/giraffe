
import os
import psutil
from giraffe.common import Service

class Host_CPU_AVG(Service.Service):
    def run(self):
        avg = os.getloadavg()
        return avg

class Host_UNAME(Service.Service):
    def run(self):
        uname = os.uname()
        return uname

class Host_PHYMEM_Usage(Service.Service):
    def run(self):
        return psutil.phymem_usage()

class Host_VIRTMEM_Usage(Service.Service):
    def run(self):
        return psutil.virtmem_usage()
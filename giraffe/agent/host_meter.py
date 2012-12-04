
import os
import psutil
from giraffe.common import task

class Host_CPU_AVG(task.Task):
    def run(self):
        avg = os.getloadavg()
        return avg

class Host_UNAME(task.Task):
    def run(self):
        uname = os.uname()
        return uname

class Host_PHYMEM_Usage(task.Task):
    def run(self):
        return psutil.phymem_usage()

class Host_VIRTMEM_Usage(task.Task):
    def run(self):
        return psutil.virtmem_usage()
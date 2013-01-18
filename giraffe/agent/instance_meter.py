__author__ = 'marcus, fbahr'

import sys
import os
import subprocess
import logging
import psutil
import libvirt
import time
from datetime import datetime, timedelta
from giraffe.common.task import PeriodicMeterTask


logger = logging.getLogger("service.collector.instance_meters")


def get_instance_pid(uuid):
    """
    Returns instance PID - else, if no instance with uuid is to be found, -1
    """
    cmd = ''.join(('ps -eo pid,command | grep ', str(uuid),
                   " | grep -v grep | awk '{print $1}'"))
    output = (subprocess.check_output(cmd, shell=True)).decode('ascii')

    return int(output) if output else -1


class Instance_UPTIME(PeriodicMeterTask):
    def meter(self):
        """
        Returns a list of IDs and corresponding uptimes (in seconds) for all
        instances running on a specific host
        """
        conn = libvirt.openReadOnly(None)
        if not conn:
            logger.exception('Failed to open connection to the hypervisor.')
            sys.exit(1)

        uptimes = []
        for id in conn.listDomainsID():
            domain = conn.lookupByID(id)
            uuid = domain.UUIDString()

            pid = get_instance_pid(uuid)
            process = psutil.Process(pid)

            uptimes.append([
                uuid,
                float('%1.2f' % ((time.time() - process.create_time) * 1000))
                ])

        return uptimes


class Instance_NETWORK_IO(PeriodicMeterTask):
    def meter(self):
        """
        Returns current network I/O in byte
        """
        pass
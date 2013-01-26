__author__ = 'marcus'

import os
import sys
import subprocess
import datetime
import psutil
import libvirt


def getInstancePID(uuid):
    """
    Returns instance PID, if no running instance found with uuid, return -1
    """
    cmd = ''.join(('ps -eo pid,command | grep ', str(uuid),
                   " | grep -v grep | awk '{print $1}'"))
    output = (subprocess.check_output(cmd, shell=True)).decode('ascii')
    if not output:
        return -1
    return int(output)

conn = libvirt.openReadOnly(None)
if conn is None:
    print 'Failed to open connection to the hypervisor'
    sys.exit(1)

#try:
else:
    (model, memory, cpus, mhz, nodes, socket, cores, threads) = conn.getInfo()
    print 'System info:'
    print 'Model = %s' % model
    print 'Memory = %s' % memory
    print 'CPUs = %s' % cpus
    print 'MHZ = %s' % mhz
    print 'Nodes = %s' % nodes
    print 'Socket = %s' % socket
    print 'Cores = %s' % cores
    print 'Threads = %s' % threads
    print ' '
    print '====================================='
    print ' '

    for id in conn.listDomainsID():
        dom = conn.lookupByID(id)
        infos = dom.info()
        uuid = dom.UUIDString()
        pid = getInstancePID(uuid)
        process = psutil.Process(pid)

        # libvirt -------------------------------------------------------------
        print 'ID = %d' % id
        print 'Name =  %s' % dom.name()
        print 'UUID = %s' % uuid
        print 'OSType = %s' % dom.OSType()
        print 'State = %d' % infos[0]
        print 'Max Memory = %d' % infos[1]
        print 'Current amount of memory used = %d' % infos[2]
        print 'Number of virt CPUs = %d' % infos[3]
        print 'CPU Time (in ns) = %d' % infos[4]

        # psutil -------------------------------------------------------------
        print 'PID = %s' % pid
        print 'Status is %s' % str(process.status)
        print 'Username = %s' % process.username
        print 'Create time = {0:>s}'.format(
            datetime.datetime.fromtimestamp(process.create_time).strftime(
                "%Y-%m-%d %H:%M"))
        print 'CPU Time = %s' % list(process.get_cpu_times())
        print 'CPU Percent = %d' % process.get_cpu_percent(interval=1.0)
        #print 'CPU affinity = %s' % list(process.get_cpu_affinity())
        print 'Memory Percent = %d' % process.get_memory_percent()
        print 'Memory Info = %s' % list(process.get_memory_info())
        print 'External Memory Info = %s' % list(process.get_ext_memory_info())
        #print 'Memory Maps = %s' % list(process.get_memory_maps())
        print 'I/O Counter = %s' % list(process.get_io_counters()) # disk I/O
        #print 'Open Files = %s' % list(process.get_open_files())
        print 'Open Connectionsi = %s' % list(process.get_connections())
        print ' '

#except:
#    print 'Errror'
#    sys.exit(1)

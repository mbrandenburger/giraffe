#!/usr/bin/env python

"""
Inserts default meters into the database.
"""

import os
import sys

possible_topdir = os.path.normpath(os.path.join(os.path.abspath(
        sys.argv[0]), os.pardir, os.pardir))

if os.path.exists(os.path.join(possible_topdir, "giraffe", "__init__.py")):
    sys.path.append(possible_topdir)

from giraffe.common.config import Config
import giraffe.service.db as db
from giraffe.service.db import Meter

print 'Loading configuration.........',
config = Config("giraffe.cfg")
print '\tdone'

print 'Connecting to database........',
db = db.connect('%s://%s:%s@%s/%s' % (config.get('db', 'vendor'),
                                      config.get('db', 'user'),
                                      config.get('db', 'pass'),
                                      config.get('db', 'host'),
                                      config.get('db', 'schema')))
db.session_open()
print '\tdone'

meters = []
meters.append(Meter(name='host.cpu.load.avg_01m',
              description='as measured by os.getloadavg() for 1 minute on the host',
              type='gauge',
              unit_name='processes',
              data_type='float'))
meters.append(Meter(name='host.cpu.load.avg_05m',
              description='as measured by os.getloadavg() for 5 minutes on the host',
              type='gauge',
              unit_name='processes',
              data_type='float'))
meters.append(Meter(name='host.cpu.load.avg_15m',
              description='as measured by os.getloadavg() for 15 minutes on the host',
              type='gauge',
              unit_name='processes',
              data_type='float'))
meters.append(Meter(name='host.memory.physical',
              description='physical memory usage on the host',
              type='gauge',
              unit_name='percent',
              data_type='float'))
meters.append(Meter(name='host.memory.virtual',
              description='virtual memory usage on the host',
              type='gauge',
              unit_name='percent',
              data_type='float'))
meters.append(Meter(name='host.uptime',
              description='host uptime',
              type='cumulative',
              unit_name='seconds',
              data_type='float'))
meters.append(Meter(name='host.disk.io.read.requests',
              description='number of disk I/O read requests',
              type='cumulative',
              unit_name='requests',
              data_type='long'))
meters.append(Meter(name='host.disk.io.read.bytes',
              description='volume of disk I/O read requests',
              type='cumulative',
              unit_name='bytes',
              data_type='float'))
meters.append(Meter(name='host.disk.io.write.requests',
              description='number of disk I/O write requests',
              type='cumulative',
              unit_name='requests',
              data_type='long'))              
meters.append(Meter(name='host.disk.io.write.bytes',
              description='volume of disk I/O write requests',
              type='cumulative',
              unit_name='bytes',
              data_type='float'))
meters.append(Meter(name='host.network.io.incoming.packets',
              description='number of sent packets',
              type='cumulative',
              unit_name='packets',
              data_type='long'))
meters.append(Meter(name='host.network.io.incoming.bytes',
              description='volume of sent packets',
              type='cumulative',
              unit_name='bytes',
              data_type='float'))
meters.append(Meter(name='host.network.io.outgoing.packets',
              description='number of sent packets',
              type='cumulative',
              unit_name='packets',
              data_type='long'))
meters.append(Meter(name='host.network.io.outgoing.bytes',
              description='volume of sent packets',
              type='cumulative',
              unit_name='bytes',
              data_type='float'))
meters.append(Meter(name='inst.uptime',
              description='instance uptime',
              type='cumulative',
              unit_name='seconds',
              data_type='float'))
meters.append(Meter(name='inst.cpu.time',
              description='CPU time used by an instance',
              type='cumulative',
              unit_name='nanoseconds',
              data_type='float'))
meters.append(Meter(name='inst.cpu.time.ratio',
              description='CPU time used in relation to real time elapsed',
              type='gauge',
              unit_name='percent',
              data_type='float'))
meters.append(Meter(name='inst.cpu.percent',
              description='[[BETA]: CPU utilization; as reported from psutil]',
              type='gauge',
              unit_name='percent',
              data_type='float'))
meters.append(Meter(name='inst.memory.physical',
              description='physical memory usage of an instance',
              type='gauge',
              unit_name='percent',
              data_type='float'))
meters.append(Meter(name='inst.memory.virtual',
              description='virtual memory usage of an instance',
              type='gauge',
              unit_name='percent',
              data_type='float'))
meters.append(Meter(name='inst.disk.io.read.requests',
              description='number of disk I/O read requests',
              type='cumulative',
              unit_name='requests',
              data_type='long'))
meters.append(Meter(name='inst.disk.io.read.bytes',
              description='volume of disk I/O read requests',
              type='cumulative',
              unit_name='bytes',
              data_type='float'))
meters.append(Meter(name='inst.disk.io.write.requests',
              description='number of disk I/O write requests',
              type='cumulative',
              unit_name='requests',
              data_type='long'))              
meters.append(Meter(name='inst.disk.io.write.bytes',
              description='volume of disk I/O write requests',
              type='cumulative',
              unit_name='bytes',
              data_type='float'))
meters.append(Meter(name='inst.network.io.incoming.packets',
              description='number of received packets',
              type='cumulative',
              unit_name='packets',
              data_type='long'))
meters.append(Meter(name='inst.network.io.incoming.bytes',
              description='volume of received packets',
              type='cumulative',
              unit_name='bytes',
              data_type='long'))
meters.append(Meter(name='inst.network.io.outgoing.packets',
              description='number of sent packets',
              type='cumulative',
              unit_name='packets',
              data_type='long'))
meters.append(Meter(name='inst.network.io.outgoing.bytes',
              description='volume of sent packets',
              type='cumulative',
              unit_name='bytes',
              data_type='long'))
              
successes = 0
for meter in meters:
    print 'Insert %s........' % meter,
    db.save(meter)
    print '\tdone'
    successes += 1
db.commit()

db.session_close()
print '\nAll done - %s meters successfully inserted!' % successes

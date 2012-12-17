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
'''
meters.append(Meter(name='loadavg_1m',
              description='as measured by os.getloadavg() for 1 minute',
              unit_name='processes',
              data_type='float'))
meters.append(Meter(name='loadavg_5m',
              description='as measured by os.getloadavg() for 5 minutes',
              unit_name='processes',
              data_type='float'))
meters.append(Meter(name='loadavg_15m',
              description='as measured by os.getloadavg() for 15 minutes',
              unit_name='processes',
              data_type='float'))
'''
meters.append(Meter(name='phymem_usage',
              description='phyiscal memory usage as percentage',
              unit_name='percent',
              data_type='float'))
meters.append(Meter(name='virmem_usage',
              description='virtual memory usage as percentage',
              unit_name='percent',
              data_type='float'))

successes = 0
for meter in meters:
    print 'Insert %s........' % meter,
    db.save(meter)
    print '\tdone'
    successes += 1
db.commit()

db.session_close()
print '\nAll done - %s meters successfully inserted!' % successes

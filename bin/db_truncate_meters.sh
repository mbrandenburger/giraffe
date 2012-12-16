#!/usr/bin/env python

"""
Deletes all meters from the database - use with caution!!
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

meters = db.load(Meter)

print 'Deleting meters...............',
deletes = 0
for meter in meters:
    db.delete(meter)
    deletes += 1
print '\tdone'
db.commit()

db.session_close()
print '\nAll done - %s meters successfully deleted!' % deletes

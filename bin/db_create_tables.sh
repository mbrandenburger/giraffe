#!/usr/bin/env python

"""
__author__ = 'omihelic'

Creates all Giraffe table in the database. 
"""

import os
import sys

possible_topdir = os.path.normpath(os.path.join(os.path.abspath(
        sys.argv[0]), os.pardir, os.pardir))

if os.path.exists(os.path.join(possible_topdir, "giraffe", "__init__.py")):
    sys.path.append(possible_topdir)

from giraffe.common.config import Config
import giraffe.service.db as db
from giraffe.service.db import Base

print 'Loading configuration.........',
config = Config("giraffe.cfg")
print '\tdone'

print 'Connecting to database........',
db = db.connect('%s://%s:%s@%s/%s' % (config.get('db', 'vendor'),
                                      config.get('db', 'user'),
                                      config.get('db', 'pass'),
                                      config.get('db', 'host'),
                                      config.get('db', 'schema')))
print '\tdone'

print 'Creating tables...............',
Base.metadata.create_all(db._engine)
print '\tdone'

print '\nAll done - tables successfully created!'

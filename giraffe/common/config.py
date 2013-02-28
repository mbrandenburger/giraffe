__author__ = 'marcus, fbahr'

import os
from ConfigParser import RawConfigParser


class Config(object):  # ...RawConfigParser):

    def __init__(self, path='giraffe.cfg'):
        # RawConfigParser.__init__(self)  # < RawConfigParser = 'old-style' class

        if path == 'giraffe.cfg':
            path = os.sep.join(__file__.split(os.sep)[0:-3] + ['bin', path])

        self._config = RawConfigParser()
        self._config.read(path)

    def __getattr__(self, name):
        if hasattr(self._config, name):
            return getattr(self._config, name)
        else:
            raise AttributeError('\'Config\' object has no attribute \'%s\'' % name)

    def get(self, section, option, **kwargs):
        try:
            return self._config.get(section, option)
        except:
            return kwargs['default']

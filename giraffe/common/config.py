__author__ = 'marcus'

import ConfigParser

class Config(object):

    def __init__(self, path="giraffe.cfg"):
        self.path = path
        self.config = ConfigParser.RawConfigParser()
        self.config.read(self.path)

    def get(self, section, item):
        return self.config.get(section, item)

    def getint(self, section, item):
        return self.config.getint(section, item)


__author__ = 'fbahr'

from giraffe.common.config import Config

import unittest


class ConfigTestCases(unittest.TestCase):

    def setUp(self):
        pass

    def test_config(self):
        Config("giraffe.cfg")


if __name__ == '__main__':
    unittest.main()

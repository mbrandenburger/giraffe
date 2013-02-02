__author__ = 'marcus'

from giraffe.common.crypto import createHash
from giraffe.common.crypto import checkHash
from giraffe.common.crypto import decryptHash
from giraffe.common.crypto import encryptHash
import unittest


class TestSequenceFunctions(unittest.TestCase):
    def setUp(self):
        pass

    def test_createHash(self):
        testMessage1 = "Just a test message"
        assert createHash(testMessage1) is not None

    def test_checkHash(self):
        testMessage1 = "Just a test message"
        testMessage1hash = createHash(testMessage1)
        testMessage2 = "message test a just"
        testMessage2hash = createHash(testMessage2)

        assert checkHash(testMessage1hash, testMessage1) is True
        assert checkHash(testMessage2hash, testMessage2) is True
        assert checkHash(testMessage1hash, testMessage2) is False
        assert checkHash(testMessage2hash, testMessage1) is False
        assert checkHash(testMessage2, testMessage2) is False

    def test_encryptHash(self):
        secret1 = "67999C243F4D79A707CE48E62CB068A6"
        secret2 = "F35A1B12E89BF4EC9F59C2533CD0F289"

        testMessage1 = "Just a test message"
        testMessage2 = "message test a just"

        testMessage1hash = createHash(testMessage1)
        testMessage2hash = createHash(testMessage2)

        cypher1 = encryptHash(secret1, testMessage1hash)
        cypher12 = encryptHash(secret1, testMessage2hash)
        cypher2 = encryptHash(secret2, testMessage2hash)
        cypher21 = encryptHash(secret2, testMessage1hash)

        assert cypher1 is not cypher2
        assert cypher1 is not cypher12
        assert cypher21 is not cypher1

    def test_decryptHash(self):
        secret1 = '67999C243F4D79A707CE48E62CB068A6'
        secret2 = 'F35A1B12E89BF4EC9F59C2533CD0F289'

        testMessage1 = "Just a test message"

        testMessage1hash = createHash(testMessage1)
        testMessage1cypher = encryptHash(secret1, testMessage1hash)

        assert testMessage1hash == decryptHash(secret1, testMessage1cypher)
        assert testMessage1hash != decryptHash(secret2, testMessage1cypher)


if __name__ == '__main__':
    unittest.main()

__author__ = 'marcus'

from Crypto.Hash import MD5
from Crypto.Cipher import AES


def createHash(message):
    return MD5.new(message).digest()


def checkHash(hash, message):
    return (hash == createHash(message))


def encryptHash(secret, hash):
    return AES.new(secret, AES.MODE_ECB).encrypt(hash)


def decryptHash(secret, ciphertext):
    return AES.new(secret, AES.MODE_ECB).decrypt(ciphertext)

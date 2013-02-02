__author__ = 'marcus'

from Crypto.Hash import MD5
from Crypto.Cipher import AES


def createHash(message):
    return MD5.new(message).digest()


def checkHash(hash, message):
    return (hash == createHash(message))


def encryptHash(secret, hash):
    return AES.new(secret, AES.MODE_ECB).encrypt(hash)


def decryptHash(secret, cipher):
    return AES.new(secret, AES.MODE_ECB).decrypt(cipher)


def createSignature(message, secret):
    return encryptHash(secret, createHash(message))


def validateSignature(message, secret, signature):
    return createHash(message) == decryptHash(secret, signature)
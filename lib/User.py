from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_OAEP
import random
import functools

class User:
    MAX_ITERATED_ENCRYPTIONS = 3 # Limit the blow-up of the final message size

    '''
    Unused, but I'm leaving this here since I learned something cool from it.

    One of the problems I spotted with the "anonymous public key sharing" algorithm was that it checked for the
    "success" of a decryption. This made no sense to me since to check for success you would have to know some part
    of the message. The only way I saw to do this was to append on a checkphrase ... which turns out to be _sort of_
    what OAEP does anyway (the padding method is more sophisticated).

    So yeah, I was pretty surprised when I got a ValueError for the wrong key, but at least now I know.
    '''
    CHECKPHRASE = "SUPERSECRETCHECKPHRASE"

    '''
    From https://pycryptodome.readthedocs.io/en/latest/src/cipher/oaep.html#Crypto.Cipher.PKCS1_OAEP.PKCS1OAEP_Cipher.encrypt:
        The message to be encrypted can have length no longer than the RSA modulus (in bytes) minus 2,
        minus twice the hash output size (which by default is SHA-1).
    
    We fix the RSA modulus to be 2048-bits (User.RSA_MODULUS), which is 256 bytes
    SHA-1 has an output length of 160 bits, which is 20 bytes (See https://en.wikipedia.org/wiki/SHA-1)

    Ultimately this max message length (in bytes) of: 256 - 2 - 2 * 20 = 214 bytes
    '''
    MAX_MESSAGE_BYTES = 214
    RSA_MODULUS = 2048
    RSA_MODULUS_BYTES = RSA_MODULUS // 8

    def __init__(self, name):
        self.__generateKeyPair()
        self.__messageLog = []
        self.__tempMessageLog = []
        self.__neighbours = []
        self.__allPublicKeys = []

        self.name = name

    def __generateKeyPair(self):
        """Generates the private/public key pair for the user.
        Arguably unneeded layer of indirection, but if I argue with myself it would make 
        me look weird.
        """
        key = RSA.generate(User.RSA_MODULUS)
        self.__privateKey = key
        self.__publicKey = key.publickey()

    def addNeighbour(self, user):
        self.__neighbours.append(user)

    def receive(self, message):
        self.__messageLog.append(message)

    def sendToNeighbours(self, message):
        for neighbour in self.__neighbours:
            neighbour.receive(message)

    def publishKeyForAnonymousMessaging(self):
        key = RSA.generate(User.RSA_MODULUS)
        self.privateKeyForAnonymousMessaging = key
        self.publicKeyForAnonymousMessaging = key.publickey()
        self.sendToNeighbours(self.publicKeyForAnonymousMessaging)
    
    def publishEncryptedPublicKey(self, n):
        publickeys = [ self.__messageLog.pop(0) for _ in range(n-1) ]
        publickeys.append(self.publicKeyForAnonymousMessaging)

        random.shuffle(publickeys) # Side note: I hate that this mutates the list

        encryptedPublicKey = self.__publicKey.exportKey()
        for key in publickeys[:User.MAX_ITERATED_ENCRYPTIONS]:
            chunks = [encryptedPublicKey[i:i+User.MAX_MESSAGE_BYTES] for i in range(0, len(encryptedPublicKey), User.MAX_MESSAGE_BYTES)]
            encryptedChunks = [PKCS1_OAEP.new(key).encrypt(chunk) for chunk in chunks]
            encryptedPublicKey = functools.reduce(lambda x, y: x + y, encryptedChunks)

        self.sendToNeighbours(encryptedPublicKey)
        self.__messageLog.append(encryptedPublicKey)

    def decryptEncryptedPublicKeysAndPublishIfSuccessful(self, n):
        publickeys = [ self.__messageLog.pop(0) for _ in range(n) ]
        
        for key in publickeys:
            chunks = [key[i:i+User.RSA_MODULUS_BYTES] for i in range(0, len(key), User.RSA_MODULUS_BYTES)]
            try:
                decryptedChunks = [PKCS1_OAEP.new(self.privateKeyForAnonymousMessaging).decrypt(chunk) for chunk in chunks]
                decryptedChunks = functools.reduce(lambda x, y: x + y, decryptedChunks)
                self.sendToNeighbours(decryptedChunks)
                self.__messageLog.append(decryptedChunks)
            except ValueError:
                continue 

    def savePublicKeys(self, n):
        self.__allPublicKeys = [ self.__messageLog.pop(0) for _ in range(n) ]



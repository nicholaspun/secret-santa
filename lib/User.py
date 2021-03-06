from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_OAEP
import random
import functools

class User:
    """Individual nodes in the network.

    Also, the people who are going to playing the Secret Santa game.

    Attributes:
    -----------
    name : String

    Methods:
    --------
    addNeighbour(user) : User -> None
        Adds user as a neighbour

    receive(message) : String -> None
        Puts message into message log

    sendToNeighbours(message) : String -> None
        Sends message to all neighbours

    publishKeyForAnonymousMessaging() : None
        Preparation step for the sub-algorithm given in https://math.stackexchange.com/a/2897431

    publishEncryptedPublicKey(n) : Integer -> None
        Encrypts own public key User.MAX_ITERATED_ENCRYPTION # of times before sending to all neighbours

    decryptEncryptedPublicKeysAndPublishIfSuccessful(n) : Integer -> None
        Decrypts the top n messages and publishes to all neighbours if the decryption is successful

    savePublicKeys(n) : Integer -> None
        Save the top n messages (which we assume are the public keys of everyone in the game)

    publishName() : [Integer] -> None
        Encrypts name using the public key specified in the derangement and publishes to all neighbours

    revealBuddy() : None
        Decrypts all the messages in queue and prints a message if one successfully reveals a name of a user
    """

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
        """Adds user as a neighbour
        
        Parameters:
        -----------
        user : User

        """
        self.__neighbours.append(user)

    def receive(self, message):
        """Puts message into message log
        
        Parameters:
        -----------
        message : String
        
        """
        self.__messageLog.append(message)

    def sendToNeighbours(self, message):
        """Sends message to all neighbours"""
        for neighbour in self.__neighbours:
            neighbour.receive(message)

    def publishKeyForAnonymousMessaging(self):
        """Preparation step for the sub-algorithm given in https://math.stackexchange.com/a/2897431
        
        Generates an RSA public/private key pair and sends the publickey to all neighbours.
        """
        key = RSA.generate(User.RSA_MODULUS)
        self.privateKeyForAnonymousMessaging = key
        self.publicKeyForAnonymousMessaging = key.publickey()
        self.sendToNeighbours(self.publicKeyForAnonymousMessaging)
    
    def publishEncryptedPublicKey(self, n):
        """Encrypts own public key User.MAX_ITERATED_ENCRYPTION # of times before sending to all neighbours
        
        Assumes that (n-1) public keys have been received from the other users in the game.
        Randomly selects User.MAX_ITERATED_ENCRYPTIONS no. of keys to iteratively encrypt user's own public key.
        The resulting message is then sent out to all neighbours.
        The goal here is to prevent the other users from knowing who sent out which public key.
        
        Parameters:
        -----------
        n : Integer
            Total number of users in the Secret Santa game (including ourselves)
        """
        publickeys = [ self.__messageLog.pop(0) for _ in range(n-1) ]
        publickeys.append(self.publicKeyForAnonymousMessaging)

        random.shuffle(publickeys) # Side note: I hate that this mutates the list

        encryptedPublicKey = self.__publicKey.exportKey()
        for key in publickeys[:min(n, User.MAX_ITERATED_ENCRYPTIONS)]:
            chunks = [encryptedPublicKey[i:i+User.MAX_MESSAGE_BYTES] for i in range(0, len(encryptedPublicKey), User.MAX_MESSAGE_BYTES)]
            encryptedChunks = [PKCS1_OAEP.new(key).encrypt(chunk) for chunk in chunks]
            encryptedPublicKey = functools.reduce(lambda x, y: x + y, encryptedChunks)

        self.sendToNeighbours(encryptedPublicKey)
        self.__messageLog.append(encryptedPublicKey)

    def decryptEncryptedPublicKeysAndPublishIfSuccessful(self, n):
        """Decrypts the top n messages and publishes to all neighbours if the decryption is successful.

        The resulting message from User.publishEncryptedPublicKey(n) is wrapped in multiple encryptions (like an onion).
        This function is performed as many times as there were encryptions, until each encryption layer is decrypted.
        
        Here, we perform a single round of decryption. 
        If the decryption using our private key is successful (pycryptodome does this automatically for us by checking the
        padding, as specified in https://tools.ietf.org/html/rfc2437), the resulting message is sent to all neighbours

        Parameters:
        -----------
        n : Integer
            Total number of users in the Secret Santa game (including ourselves)
        """
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
        """Save the top n messages (which we assume are the public keys of everyone in the game)
        
        Parameters:
        -----------
        n : Integer
            Total number of users in the Secret Santa game (including ourselves)
        """
        self.__allPublicKeys = [ self.__messageLog.pop(0) for _ in range(n) ]

    def publishName(self, derangement):
        """Encrypts name using the public key specified in the derangement and publishes to all neighbours

        Assumes that everyone has the same ordering of publickeys (this is true in our case).
        Our position in the derangement is then exactly our order in the list of publickeys, and
        our secret santa is defined to be whoever we are mapped to in the given derangement.

        Parameters:
        -----------
        derangement : [Integer]
        """
        
        selfIdx = None
        for idx, key in enumerate(self.__allPublicKeys):
            if key == self.__publicKey.exportKey():
                selfIdx = idx
                break
        
        secretSantaPublicKey = RSA.importKey(self.__allPublicKeys[derangement[selfIdx]])
        self.sendToNeighbours(PKCS1_OAEP.new(secretSantaPublicKey).encrypt(bytes(self.name, 'utf-8')))

    def revealBuddy(self):
        """Decrypts all the messages in queue and prints a message if one successfully reveals a name of a user.

        This doesn't technically align with the spirit of the game, but since this is just a demo, this
        function reveals that the scheme has worked.
        """
        while len(self.__messageLog) != 0:
            try:
                name = PKCS1_OAEP.new(self.__privateKey).decrypt(self.__messageLog.pop(0))
                print("{} paired with {}".format(self.name, name.decode('utf-8')))
            except ValueError:
                continue

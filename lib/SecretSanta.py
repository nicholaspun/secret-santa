from lib.User import User
from lib.util import createDerangment

class SecretSanta:
    """Manages the Secret Santa game (? - Not the right word, but couldn't think of a better one)

    This is technically cheating as having a manager means we use a third party ...
    but we're close enough to the real deal. Just suppose there existed a protocol 
    that would run the Secret Santa algorithm and this is exactly the protocol 
    with extra steps :P.

    Attributes
    ----------

    Methods
    -------
    registerUser(name) : String -> None
        Creates and registers user with the given name

    initializeNetwork() : None
        Sets neighbours for every user

    createDerangement() : None
        Pairs users off to play Secret Santa!
    """
    def __init__(self):
        self.__users = []

    def registerUser(self, name):
        """Creates and registers user with the given name.

        This is a weird implementation since users cannot exist outside
        of this protocol.
        But, eh ¯\\\\\_(ツ)\\_/¯

        Parameters:
        ----------
        name : String

        Returns:
        --------
        None
        """
        user = User(name)
        self.__users.append(user)

    def initializeNetwork(self):
        """Set neighbours for every user.
        We currently just build a complete graph for the network structure.
        """
        for i in range(len(self.__users)):
            for j in range(len(self.__users)): 
                '''
                Oh gods, O(n^2). The worst amount of edges to have. Darn you complete graph!

                Wait, complete graph you say? Isn't that not ideal for this problem?
                Well.
                Yes.
                But, small steps :)
                Let's just assume that all the users here are trustworthy and don't keep the entire 
                message log so it's ok.
                '''
                if i != j: 
                    self.__users[i].addNeighbour(self.__users[j])

    def createDerangement(self):
        """Pairs users off to play Secret Santa!

        Follows the algorithm created here: https://math.stackexchange.com/a/2897431.
        """
        self.__publishPublicKey()
        
        # Let's just ignore the random seed part of the algorithm
        derangement = createDerangment(len(self.__users))        
        for user in self.__users:
            user.publishName(derangement)

        # For demonstration purposes, this prints all pairings
        for user in self.__users:
            user.revealBuddy()

    def __publishPublicKey(self):
        """Implements the sub-algorithm (from https://math.stackexchange.com/a/2897431) to anonymously
        share everyone user's public key.
        """
        for user in self.__users:
            user.publishKeyForAnonymousMessaging()

        for user in self.__users:
            user.publishEncryptedPublicKey(len(self.__users))

        for _ in range(User.MAX_ITERATED_ENCRYPTIONS):
            for user in self.__users:
                user.decryptEncryptedPublicKeysAndPublishIfSuccessful(len(self.__users))

        for user in self.__users:
            user.savePublicKeys(len(self.__users))

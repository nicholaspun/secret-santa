from lib.User import User

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
    """
    def __init__(self):
        self.__users = []

    def registerUser(self, name):
        """Creates and registers user with the given name

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

        Parameters:
        ----------
        None

        Returns:
        -------
        None
        """
        for i in range(len(self.__users)):
            for j in range(len(self.__users)): 
                '''
                Oh gods, O(n^2). Best we're going to do though since there are O(n^2) edges in a
                complete graph.

                Wait, complete graph you say? Isn't that not ideal for this problem?
                Well.
                Yes.
                But, all the users here are trustworthy and don't keep infinite message log so it's ok :) 
                '''
                if i != j: 
                    self.__users[i].addNeighbour(self.__users[j])

    def createDerangement(self):
        self.__publishPublicKey()

    def __publishPublicKey(self):
        for user in self.__users:
            user.publishKeyForAnonymousMessaging()

        for user in self.__users:
            user.publishEncryptedPublicKey(len(self.__users))

        for _ in range(User.MAX_ITERATED_ENCRYPTIONS):
            for user in self.__users:
                user.decryptEncryptedPublicKeysAndPublishIfSuccessful(len(self.__users))

        for user in self.__users:
            user.savePublicKeys(len(self.__users))
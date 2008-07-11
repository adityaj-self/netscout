class Host:
    """
    The host class conatins details pertaining to hosts on the network.
    Holds IP Address, PORT, LDAP logins and information about P2P and HTTP activity
    """
  
    def __init__(self,ipAddr,hubIPORPort,hubType):
        self.ipAddr=ipAddr
        if (hubType == "Client"):
            self.hubAddr=hubIPORPort
        else:
            self.port=hubIPORPort
        self.p2pActive=False
        self.httpActive=False
            

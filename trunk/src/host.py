import logging
from utils import getCfg
import utils
import time
import os
import const

sessionUsers={} #Host-LDAP pair
knownHost={}
knownUser={}


def addHostActivity(ip,user,hwaddr):
    hostid=addHost(ip)
    userid=addUser(user)
    t=(int(time.time()),hostid,userid,hwaddr)
    conn = utils.connectDB()
    cur = conn.cursor()
    cur.execute("insert into hostAct(timestamp,hostID,userID,hwaddr) values (?,?,?,?) ",t)
    cur.execute("select max(hostActID) from hostAct")
    maxID = int(cur.fetchone()[0])
    conn.close()
    return maxID

def extractUserID(hostIP):
    """
    Obtain user id via HTTP request packets
    """
    logging.debug("Checking if User ID is already known")
    for key,value in sessionUsers.items():
        if key == hostIP:
            logging.debug("UserID Known: "+sessionUsers[hostIP])
            return sessionUsers[hostIP]
    logging.debug('Obtaining User id for: '+str(hostIP))
    logging.debug('Scanning HTTP requests for : '+hostIP)
    #Look for HTTP request packets and then via tshark extract the proxy user id (cut out the password)
    os.system("tcpdump -s0 -i "+getCfg("interface")+" 'host "+hostIP\
             +" and tcp dst port 80' -c "+getCfg("userHUB")+" -w - | "\
             +" tshark -i - -T fields -e http.authbasic -R \"http.request && http.authbasic\" | cut -f1 -d ':'| sort -u > "+getCfg("uidTshark"))
    fuid=open(getCfg("uidTshark"),'r')
    userName=fuid.readline()
    fuid.close()
    sessionUsers[hostIP] = userName
    return userName

def getHostsFromDB():
    """
    Read Host data from DB
    """
    logging.debug("getting existing host info")
    conn = utils.connectDB()
    cur = conn.cursor()
    cur.execute("select * from host")
    dbHost = cur.fetchall()
    logging.debug("Found existing "+str(len(dbHost))+" hosts")
    for i in range(len(dbHost)):
        knownHost[dbHost[i][const.ID_IND]] = dbHost[i][const.NAME_IND]
    conn.close()

def getUsersFromDB():
    """
    Read User name data from DB
    """
    logging.debug("getting existing user info")
    conn = utils.connectDB()
    cur = conn.cursor()
    cur.execute("select * from user")
    dbUser = cur.fetchall()
    logging.debug("Found existing "+str(len(dbUser))+" users")
    for i in range(len(dbUser)):
        knownUser[dbUser[i][const.ID_IND]] = dbUser[i][const.NAME_IND]
    conn.close()
    

def existsHost(host):
    """
    Return true and ID, or false and -1 based on presense of HOST IP
    """
    for key,value in knownHost.items():
        if value == host:
            logging.debug("Host seen in this session")
            return (True,key)    
    logging.debug("Host not been seen in this session")
    return (False,-1)
       

def existsUser(user):
    """
    Return true and ID, or false and -1 based on presense of USER Name
    """
    for key,value in knownUser.items():
        if value == user:
            logging.debug("User seen in this session")
            return (True,key)    
    logging.debug("User not been seen in this session")
    return (False,-1)

def addHost(host):
    """
    Add a new host IP (checking if exists first)
    """
    logging.debug("adding host"+host)
    (exists,id)=existsHost(host)
    if (exists):
        return id
    else:
        conn = utils.connectDB()
        cur = conn.cursor()
        cur.execute("insert into host(hostIP) values (?)",(host,))
        cur.execute("select max(hostID) from host")
        maxID = int(cur.fetchone()[0])
        knownHost[maxID] = host
        conn.close()
        return maxID

def addUser(user):
    """
    Add a new user (checking if exists first)
    """
    (exists,id)=existsUser(user)
    if (exists):
        return id
    else:
        conn = utils.connectDB()
        cur = conn.cursor()
        cur.execute("insert into user(userName) values (?)",(user,))
        cur.execute("select max(userID) from user")
        maxID = int(cur.fetchone()[0])
        knownUser[maxID] = user
        conn.close()
        return maxID
    
def getUserNameByID(userID):
    """
    Return the HOST IP address by the ID
    """
    pass

def getHostNameByID(hostID):
    """
    Return the HOST IP address by the ID
    """
    pass



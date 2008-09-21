import logging
import time
import os

import const
from utils import getCfg
import utils

sessionUsers={} #Host-LDAP pair
dbHosts={} #Hosts in the database
dbUsers={} # users in the database

def addHostActivity(ip,user):
    hostid=addHost(ip)
    userid=addUser(user)
    t=(int(time.time()),hostid,userid)
    conn = utils.connectDB()
    cur = conn.cursor()
    cur.execute("insert into hostAct(timestamp,hostID,userID) values (?,?,?) ",t)
    cur.execute("select max(hostActID) from hostAct")
    maxID = int(cur.fetchone()[0])
    conn.close()
    return maxID,hostid

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
    hostData = cur.fetchall()
    logging.debug("Found existing "+str(len(hostData))+" hosts")
    for i in range(len(hostData)):
        dbHosts[int(hostData[i][const.ID_IND])] = hostData[i][const.NAME_IND]
    conn.close()
    return dbHosts

def getUsersFromDB():
    """
    Read User name data from DB
    """
    logging.debug("getting existing user info")
    conn = utils.connectDB()
    cur = conn.cursor()
    cur.execute("select * from user")
    userData = cur.fetchall()
    logging.debug("Found existing "+str(len(userData))+" users")
    for i in range(len(userData)):
        dbUsers[userData[i][const.ID_IND]] = userData[i][const.NAME_IND]
    conn.close()
    return dbUsers
    

def existsHost(host):
    """
    Return true and ID, or false and -1 based on presense of HOST IP
    """
    for key,value in dbHosts.items():
        if value == host:
            logging.debug("Host seen in this session")
            return (True,key)    
    logging.debug("Host not been seen in this session")
    return (False,-1)
       

def existsUser(user):
    """
    Return true and ID, or false and -1 based on presense of USER Name
    """
    for key,value in dbUsers.items():
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
        dbHosts[maxID] = host
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
        dbUsers[maxID] = user
        conn.close()
        return maxID
    
def getUserNameByID(userID):
    """
    Return the HOST IP address by the ID
    """
    for key,value in dbUsers.items():
        if userID == key:
            return value

def getHostNameByID(hostID):
    """
    Return the HOST IP address by the ID
    """
    for key,value in dbHosts.items():
        if hostID == key:
            return value



import logging
from utils import getCfg
import utils
import time

sessionUsers={}
knownHost=[]
knownUser=[]

def addHostActivity(ip,user,hwaddr):
    hostid=addHost(ip)
    userid=addUser(user)
    
    t=(int(time.time()),hostid,userid,hwaddr)
    conn = utils.connectDB()
    cur = conn.cursor()
    cur.execute("insert into hostAct(timestamp,hostID,userID,hwaddr) values ",t)
    cur.execute("select max(hostActID) from hostAct")
    return maxID


def addFileList(hostActID,fileList):
    conn = utils.connectDB()
    cur = conn.cursor()
    cur.execute("insert into fileList(hostActID,fileList) values ",(hostActID,fileList))

def extractUserID(hostIP):
    """
    Obtain user id via HTTP request packets
    """
    logging.debug("Checking if User ID is already known")
    if(hostIP in sessionUsers):
        logging.debug("UserID Known: "+sessionUsers[hostIP])
        return sessionUsers[hostIP]
    logging.debug('Obtaining User id for: '+hostIP)
    logging.debug('Scanning HTTP requests for : '+hostIP)
    #Look for HTTP request packets and then via tshark extract the proxy user id (cut out the password)
    os.system("tcpdump -s0 -i "+getCfg("interface")+" 'host "+hostIP\
             +" and tcp dst port 80' -c "+getCfg("userHUB")+" -w - | "\
             +" tshark -r - -T fields -e http.authbasic -R \"http.request && http.authbasic\" | cut -f1 -d ':'| sort -u > "+getCfg("uidTshark"))
    fuid=open(getCfg("uidTshark"),'r')
    userName=fuid.readline()
    fuid.close()
    sessionUsers[hostIP] = userName
    return userName

def getHostsFromDB():
    """
    Read Host data from DB
    """
    conn = utils.connectDB()
    cur = conn.cursor()
    cur.execute("select * from host")
    
    conn.close()

def getUsersFromDB():
    """
    Read User name data from DB
    """
    conn = utils.connectDB()
    cur = conn.cursor()
    cur.execute("select * from user")
    
    conn.close()
    

def existsHost(host):
    """
    Return true and ID, or false and -1 based on presense of HOST IP
    """
    if (host in knownHost):
        return (True,knownHost.index(host))
    else:
        return (False,-1)

def existsUser(user):
    """
    Return true and ID, or false and -1 based on presense of USER Name
    """
    if (host in knownUser):
        return (True,knownUser.index(user))
    else:
        return (False,-1)


def addHost(host):
    """
    Add a new host IP (checking if exists first)
    """
    (exists,id)=existsHost(host)
    if (exists):
        return id
    else:
        conn = utils.connectDB()
        cur = conn.cursor()
        cur.execute("insert into host(hostIP) values = ?",host)
        cur.execute("select max(hostID) from host")
        cur.fetchone[0]
        knownHost.append(maxID,host)
        conn.close()
        

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
        cur.execute("insert into host(hostIP) values = ?",host)
        cur.execute("select max(hostID) from host")
        cur.fetchone[0]
        knownHost.append(maxID,host)
        conn.close()
        return maxID
    
def getUserNameByID(userID):
    """
    Return the HOST IP address by the ID
    """

def getHostNameByID(hostID):
    """
    Return the HOST IP address by the ID
    """


def hostActivity(hostID,userID,hwAddr):
    """
    Add host activity
    """
    pass


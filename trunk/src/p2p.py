import os
import re
import logging
import utils
from utils import getCfg

import host


def addP2PAct():
    pass

def dcpp():
    """
    DC++ traffic analysis
    """
    host.getHostsFromDB()
    identifyDCPPHUBs()
    hubDataList=utils.fileToArray(get("hubColFile"), get("hubNCol"))
    hubIPList = hubDataList[0]
    hubPortList = hubDataList[1]
    #Get LDAP
    i=0
    for ip in hubIPList:
        hostActID=host.addHostActivity(ip, host.extractUserID(i), hwaddr)
        #Get files
        videoList=getHubFiles(hostIP)
        #Get Client
        clientHostList=identifyClients(hubIP, hostPort)
        #Add host activity
        for cip in clientHostList:
            addP2PAct(host.addHostActivity(ip, host.extractUserID(cip), hwaddr),1,hostActID)
        #Add p2p activity
        addP2PAct(hostActID,0,hubPortList[i])
        i=i+1

def identifyDCPPHUBs():
    logging.debug("Looking for DC++ HUBS")
    logging.debug("Listening for MyINFO packets")
    os.system("ngrep -i -q -R -d "+getCfg("interface")+" -n "+getCfg("myinfo")+" -w MyINFO -O "+getCfg("myinfoDump")+"> /dev/null")
    logging.debug("Obtaining DC++ HUBS IP and PORT")
    os.system("ngrep -i -q -R -I "+getCfg("myinfoDump")+" -w GetNickList -v | grep \"[0-9].[0-9].[0-9].[0-9] [ ->]\" | awk -F\" \" '{print $2}'| awk -F\":\" '{print $1\" \"$2}' | sort -u > "+getCfg("hubColFile"))

def identifyClients(hubIP,hostPort):
    logging.debug('Scanning for P2P clients')
    logging.debug('Scanning for P2P clients for HUB: '+hubIP)
    os.system("ngrep -q -i -d "+getCfg("interface")+" '' -W byline 'host "+hubIP+" and tcp src port "+hostPort+"' -n "+getCfg("hubClient")\
             +" | grep \"[0-9].[0-9].[0-9].[0-9] [ ->]\" | awk -F\" \" '{print $4}' | awk -F\":\" '{print $1}' |sort -u > "+getCfg("clientFile"))
    clientHostList=self.fileToHost(self.CLT_FILE, self.CLT_NCOL)
    logging.debug('Getting LDAP IDs of users acting as P2P Clients')
    for i in range(len(clientHostList)):
        host.extractUserID(clientIP)
    return clientHostList

def getHubFiles(hostIP):
    logging.info('Getting File List for HUB: '+hostIP)
    os.system("ngrep -i -q -R -d "+getCfg("interface")+" -W byline -n "+getCfg("")+" -w '\$SR' 'src host "+hostIP+"' > "+self.SR_DUMP)
    allFileData = open(self.SR_DUMP,'r').read()
    p=re.compile('\|\$SR [0-9A-Z_]*', re.DOTALL | re.IGNORECASE)
    q=re.compile('[0-9]/[0-9]\.TTH:[0-9A-Z]*', re.DOTALL | re.IGNORECASE)
    markstart=p.sub(' FILESTART',allFileData)
    markend=q.sub(' FILEEND',markstart)
    fileList=re.findall('FILESTART.*?FILEEND', markend, re.DOTALL | re.IGNORECASE)
    videoList=[]
    logging.info('Searching for requested file extensions')
    extension = getCfg("ext")
    for j in range(len(fileList)):
         fromInd=fileList[j].rfind('\\')
         fileList[j]=fileList[j].lower()
         fromInd=fromInd+1
         toInd=0
         for m in extension:
             logging.debug("extension: "+m)         
             if (m in fileList[j]):
                 toInd=fileList[j].rfind(m)
                 toInd=toInd+len(m)
                 if (fileList[j][fromInd:toInd].strip()!='' and toInd!=0):
                     videoList.append(fileList[j][fromInd:toInd])
                 logging.debug("Files found as of now: "+videoList)
    return videoList


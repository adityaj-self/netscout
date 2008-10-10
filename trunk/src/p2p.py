## Author - Aditya Joshi
## File - p2p.py

import os
import re
import logging

import utils
from utils import getCfg
import host
import const

def addP2PAct(hostActID,hubType,portOrServerID):
    """
    Add p2p activity
    """
    t = (hostActID,hubType,portOrServerID)
    conn = utils.connectDB()
    cur = conn.cursor()
    cur.execute("insert into p2pAct(hostActID,hubType,portNumorHubIP) values (?,?,?) ",t)
    conn.close()

def dcpp():
    """
    DC++ traffic analysis
    """
    identifyDCPPHUBs()
    hubDataList=utils.fileToArray(getCfg("hubColFile"), const.HUB_COL_CNT)
    hubIPList = hubDataList[0]
    hubPortList = hubDataList[1]
    #Get LDAP
    i=0
    for ip in hubIPList:
        port = hubPortList[i]
        (hostActID,hostID)=host.addHostActivity(ip, host.extractUserID(ip))
        #Get files
        files=getHubFiles(ip)
        #Get Client
        clientHostList=identifyClients(ip, port)
        #Add host activity
        logging.debug("Adding client information")
        for cip in clientHostList:
            addP2PAct(host.addHostActivity(cip, host.extractUserID(cip))[const.AH_HOSTACTID],const.CLIENT,hostID)
        logging.debug("Adding hub information")
        #Add p2p activity
        addP2PAct(hostActID,const.SERVER,port)
        addFileList(hostActID, files)
        i=i+1


def addFileList(hostActID,files):
    conn = utils.connectDB()
    cur = conn.cursor()
    t = (hostActID,files)
    cur.execute("insert into fileList(hostActID,fileList) values (?,?) ",t)
    conn.close()

def identifyDCPPHUBs():
    logging.debug("Looking for DC++ HUBS")
    logging.debug("Listening for MyINFO packets")
    os.system("ngrep -i -q -R -d "+getCfg("interface")+" -n "+getCfg("myinfo")+" -w MyINFO -O "+getCfg("myinfoDump")+"> /dev/null")
    logging.debug("Obtaining DC++ HUBS IP and PORT")
    os.system("ngrep -i -q -R -I "+getCfg("myinfoDump")+" -w GetNickList -v | grep \"[0-9].[0-9].[0-9].[0-9]:[0-9]* [ ->]\" | awk -F\" \" '{print $2}'| awk -F\":\" '{print $1\" \"$2}' | sort -u > "+getCfg("hubColFile"))

def identifyClients(hubIP,hostPort):
    logging.debug('Scanning for P2P clients')
    logging.debug('Scanning for P2P clients for HUB: '+hubIP)
    os.system("ngrep -q -i -d "+getCfg("interface")+" '' -W byline 'host "+hubIP+" and tcp src port "+hostPort+"' -n "+getCfg("hubClient")\
             +" | grep \"[0-9].[0-9].[0-9].[0-9] [ ->]\" | awk -F\" \" '{print $4}' | awk -F\":\" '{print $1}' |sort -u > "+getCfg("clientFile"))
    clientHostData=utils.fileToArray(getCfg("clientFile"), const.CLNT_COL_CNT)
    clientIPList=clientHostData[0]
    logging.debug("clientList: "+str(clientIPList))
    return clientIPList

def getHubFiles(hostIP):
    logging.info('Getting File List for HUB: '+hostIP)
    os.system("ngrep -i -q -R -d "+getCfg("interface")+" -W byline -n "+getCfg("sr")+" -w '\$SR' 'src host "+hostIP+"' | grep -v \"[0-9].[0-9].[0-9].[0-9]:[0-9]*\" > "+getCfg("srDump"))
    allFileData = open(getCfg("srDump"),'r').read()
    allFileData = allFileData.replace("\n","")
    p=re.compile('\|\$SR [0-9A-Z_]*', re.DOTALL | re.IGNORECASE)
    q=re.compile('[0-9]/[0-9]\.TTH:[0-9A-Z]*', re.DOTALL | re.IGNORECASE)
    markstart=p.sub(' FILESTART',allFileData)
    markend=q.sub(' FILEEND',markstart)
    fileList=re.findall('FILESTART.*?FILEEND', markend, re.DOTALL | re.IGNORECASE)
    filteredFileList=[]
    logging.info('Searching for requested file extensions')
    extension = getCfg("ext").split(',')
    logging.debug("extensions: "+str(extension))
    for j in range(len(fileList)):
         fromInd=fileList[j].rfind('\\')
         fileList[j]=fileList[j].lower()
         fromInd=fromInd+1
         toInd=0
         for m in extension:
             if (m in fileList[j]):
                 toInd=fileList[j].rfind(m)
                 toInd=toInd+len(m)
                 if (fileList[j][fromInd:toInd].strip()!='' and toInd!=0):
                     filteredFileList.append(fileList[j][fromInd:toInd])
    logging.debug("videoList: "+str(filteredFileList))
    return '\n'.join(map(str,filteredFileList))


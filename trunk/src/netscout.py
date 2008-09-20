#!/usr/bin/env python

"""
Author: Aditya Joshi
"""

import sys
import os
import shutil
import logging
import sqlite3

import p2p
import utils
import http
import host

def createDirStruct():
    """
    Create the directory struccture for holding network dumps. 
    A directory of the same name (if any) is deleted and recreated.
    """
    if (os.path.exists(utils.getCfg('dataDir'))):
        logging.debug('Deleting exisitng log directories')
        shutil.rmtree(utils.getCfg('dataDir'))    
    logging.debug('Creating log directories')
    os.mkdir(utils.getCfg('dataDir'))
    os.mkdir(utils.getCfg('p2pDir'))
    os.mkdir(utils.getCfg('httpDir')) 
    
def helpInfo():
    logging.info('Usage: netscout [-i|-r] <interface> [-reset] ')

def verInfo():
    logging.info('nescout version 1.0')
    logging.critical('Ensure you are root!')

def processArgs():
    """
    Scan the input to ensure netscout is invoked with proper arguments
    """
    paramList=sys.argv
    if ("-v" in paramList):
        #In addition the file logging, DEBUG and above messages will be logged to stdout
        #Edit the Stream logger (second in the handler array to update the logging level)
        logging.getLogger().handlers[1].setLevel(logging.DEBUG)
        logging.info('Detailed Screen logging on')
        
    if ("-h" in paramList):
        helpInfo()
        sys.exit() 
        
    if ("-reset" in paramList):
        logging.warning("Resetting database! All data and configuration will be lost!")
        initDB("reset")
    else:
        initDB("check")

    """
        Ensure that the mandatory parameter '-i' or '-r' is specfied
    """ 
    if (not("-i" in paramList or "-r" in paramList or "-u" in paramList)):
        logging.error("Specify one of '-i', '-r' or -u mandatory options")
        sys.exit()
    
    if("-i" in paramList):
        interfaceInd=paramList.index("-i")+1
        interface=""
        try:
            interface=paramList[interfaceInd]
        except:
            logging.error("NO INTERFACE VALUE SPECIFIED")
            sys.exit()
        logging.info("netscout passive mode")
        utils.setCfg("mode","passive")
        utils.setCfg("interface", interface)
        return
    
    if("-r" in paramList):  
        logging.info("netscout report mode")
        report()

    if("-u" in paramList):
        logging.info("netscout web domain update mode")
        http.domainUpdate()
        updateInd=paramList.index("-u")+1
        update=""
        if (updateInd == len(paramList)-1):
            update=paramList[updateInd]
            if (update == "all"):
                logging.warning("Updating all web domains")
                utils.setCfg("update", update)
        else:
            logging.info("Updating new web domains")
            utils.setCfg("update", "")


def report():
    conn = utils.connectDB()
    conn.close()
#    hubs=self.hubHostList
#    logging.debug('P2P Analysis Stored at: '+self.P2P_ANALYSIS)
#    p2pAnalysisData='\t\tP2P Analysis Results: \n'
#    p2pAnalysisData+='\t\t--------------------\n'
#    p2pOutput=open(self.P2P_ANALYSIS,'w')
#    for i in range(len(hubs)):
#        p2pAnalysisData+='\n --------------INFO FOR HUB : '+hubs[i].ipAddr+'--------------------------\n\n'
#        p2pAnalysisData+='HUB IP'.rjust(16)+'PORT'.rjust(6)+'LDAP ID'.rjust(10)+'\n'
#        p2pAnalysisData+=hubs[i].ipAddr.rjust(16)+hubs[i].port.rjust(6)+hubs[i].loginLDAP.rjust(10)+'\n'
#        p2pAnalysisData+='\nClients connected to the HUB'+'\n'
#        clients=hubs[i].clients
#        for i in range(len(clients)):
#            p2pAnalysisData+='Client IP'.rjust(16)+'LDAP ID'.rjust(10)+'\n'
#            p2pAnalysisData+=clients[i].ipAddr.rjust(16)+clients[i].loginLDAP.rjust(10)+'\n'
#        p2pAnalysisData+='\nVideo files hosted by HUB: \n\n'
#        fileList=hubs[i].fileList
#        for k in range(len(fileList)):
#            logging.debug(fileList[k]+'\n')
#            p2pAnalysisData+=fileList[k]+'\n'
#        logging.debug('\n --------------HUB INFO END-------------------------------------\n')
#        p2pAnalysisData+='\n --------------HUB INFO END-------------------------------------\n'
#    p2pOutput.write(p2pAnalysisData)
#    p2pOutput.close()


def initDB(oper):
    """
    Check for existence of db file. If reset required then either delete or create new 
    db file and import the db schema
    """
    if (os.path.exists(utils.getCfg('nsDB'))):
        if (oper == "check"):
            logging.debug("Using existing db file")
            return
        else:
            if (oper == "reset"):
                logging.debug("Deleting database file")
                os.remove(utils.getCfg('nsDB'))
    logging.debug("Creating new db file")
    open(utils.getCfg('nsDB'),"w")
    conn = utils.connectDB()
    schemaFile = open(utils.getCfg('nsSchema'));
    conn.executescript(schemaFile.read())
    conn.commit()
    logging.info('Database reset successfully')
    schemaFile.close()
    conn.close()

def setupLog():
    """
    Perform the file and consolelogging setup
    """
    logging.basicConfig(filename='netscout.log',datefmt="%d-%m-%Y %H:%M",\
                        format="%(levelname)-8s %(asctime)+17s Line %(lineno)-4d %(module)s.%(funcName)-15s : %(message)s"\
                        ,level=logging.DEBUG,filemode="a")
    logging.info('==========Initiating netscout logging==========')
    console = logging.StreamHandler()
    console.setLevel(logging.INFO)
    formatter = logging.Formatter('%(levelname)-8s: %(message)s')
    console.setFormatter(formatter)
    logging.getLogger().addHandler(console)
    logging.debug('Screen logging on')


def checkRootPerms():
    logging.debug("Checking if root permissions available")
    os.system("tcpdump -i "+utils.getCfg("interface")+" -c 1 2> roottest 1> /dev/null")
    fid = open("roottest")
    if ("Operation not permitted" in fid.read()):
        logging.error("ROOT permissions not available. Exiting.")
        exit = True
    else:
        logging.debug("ROOT permissions available")
        exit = False
    os.remove("roottest")
    if(exit):
        sys.exit()
        
    

def main():
    """
    Main thread of execution
    """
    setupLog()
    verInfo()
    utils.readConfig()
    processArgs()
    checkRootPerms()
    createDirStruct()
    if(utils.getCfg("mode")=="passive"):
        host.getHostsFromDB()
        host.getUsersFromDB()
        if (utils.getCfg("dcppMode") == "true"):
            logging.info("Initialing DC++ P2P scouting")
            p2p.dcpp()
    
        if (utils.getCfg("httpMode") == "true"):
            logging.info("Initialing HTTP scouting")
            http.httpActivity()
    
    
    #httpModel
    #statModel
    
"""
Invoke the main thread.
"""
main()

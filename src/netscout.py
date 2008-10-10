#!/usr/bin/env python

## Author - Aditya Joshi
## File - netscout.py

"""
Author: Aditya Joshi
"""

import sys
import os
import shutil
import logging
import sqlite3
import time

import p2p
import utils
import http
import host
import const

def createDirStruct():
    """
    Create the directory structure for holding network dumps. 
    A directory of the same name (if any) is deleted and recreated.
    """
    if (os.path.exists(utils.getCfg('dataDir'))):
        logging.debug('Deleting exisitng data directories')
        shutil.rmtree(utils.getCfg('dataDir'))    
    logging.debug('Creating data directories')
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
        logging.getLogger().handlers[const.CON_HANDLE].setLevel(logging.DEBUG)
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
    cur = conn.cursor()
    logging.debug("reporting findings")
    hosts = host.getHostsFromDB()
    users = host.getUsersFromDB()
    logging.debug("len(hosts):"+str(len(hosts)))
    if (len(hosts) == 0):
	logging.info("No data available to generate report")
	sys.exit()
    for hostID,hostIP in hosts.items():
        print'\n-----------------\n'
        print'\nHOST:'+hostIP
        t = (hostID,)
        cur.execute('select * from hostAct where hostID = ?', t)
        rs = cur.fetchall()
        for i in range(len(rs)):
            print'\t Activity: '+str(i)
            print'\t User ID : '+users[rs[i][const.HA_USER_ID]].strip()
            print'\t Time    : '+time.asctime(time.localtime(int(rs[i][const.HA_TIME])))
            t = (rs[i][const.HA_ID],)
            cur.execute('select * from p2pAct where hostActID = ?', t)
            rs1 = cur.fetchall()
            for j in range(len(rs1)):
                print'\t\t P2P Act : '+str(j)
                if (rs1[j][const.P2P_HUBTYPE] == const.SERVER):
                    print'\t\t P2P Type: SERVER'
                    print'\t\t PORT    : '+str(rs1[j][const.P2P_PORT_HUBID])
                    print'\t\t FILES'
                else:
                    print'\t\t P2P Type: CLIENT'
                    print'\t\t SERVER  : '+str(host.getHostNameByID(rs1[j][const.P2P_PORT_HUBID]))
    sys.exit()


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
    logging.info('Database initialized successfully')
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
    
        if (utils.getCfg("statMode") == "true"):
            logging.info("Initialing statistical scouting")
            http.httpActivity()
    
"""
Invoke the main thread.
"""
main()

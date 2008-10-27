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
import stats
import report

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
        report.overview()

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

"""
Ensuring prerequisites exist on host 
"""

def checkPrereqs():
    exit = False
    toCheck = ["tcpdump","tshark","ngrep"]
    for prereq in toCheck:
	os.system("which "+prereq+" 2> cmdtest 1>/dev/null")
	fid = open("cmdtest")
	if ("which: no" in fid.read()):
	    logging.error(prereq+" check failed")
	    exit = True
	else:
	    logging.debug(prereq+" check ok")
    if (exit):
	sys.exit()
    logging.debug("Checking packet capturing capabilities")
    os.system("tcpdump -i "+utils.getCfg("interface")+" -c 1 2> cmdtest 1> /dev/null")
    fid = open("cmdtest")
    if ("Operation not permitted" in fid.read()):
        logging.error("Cannot capture packets. Ensure ROOT permissions are available.")
        exit = True
    else:
        logging.debug("Capture permissions available.")
    os.remove("cmdtest")
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
    checkPrereqs()
    createDirStruct()
    if(utils.getCfg("mode")=="passive"):
        host.getHostsFromDB()
        host.getUsersFromDB()
        if (utils.getCfg("dcppMode") == "true"):
            logging.info("Initializing DC++ P2P scouting")
            p2p.dcpp()
    
        if (utils.getCfg("httpMode") == "true"):
            logging.info("Initializing HTTP scouting")
            http.httpActivity()
    
        if (utils.getCfg("statMode") == "true"):
            logging.info("Initializing statistical scouting")
            stats.statActivity() 
    
"""
Invoke the main thread.
"""
main()

#!/usr/bin/env python

"""
Author: Aditya Joshi
"""

import sys
import os
import shutil
from ConfigParser import ConfigParser
import logging
import sqlite3

from utils import *

 
def createDirStruct():
    """
    Create the directory struccture for holding network dumps. 
    A directory of the same name (if any) is deleted and recreated.
    """
    try:
        dirstat=os.stat(getCfg('dataDir'))
        shutil.rmtree(getCfg('dataDir'))
    except:
        logging.info('Creating log directories')
    os.mkdir(getCfg('dataDir'))
    os.mkdir(getCfg('p2pDir'))
    os.mkdir(getCfg('httpDir')) 
    
def helpInfo():
    logging.info('nescout version 1.0')
    logging.info('Usage: netscout [-i|-r] <interface> [-reset] ')
    logging.info('Ensure you are root!')

def passiveAnalysis(conn):
    p2pmodel=p2p.P2PModel(netscout.interface,netscout.P2P_FOLDER)
    p2pmodel.getHubInfo()
    p2pmodel.printP2PAnalysis()

def processArgs():
    """
    Scan the input to ensure netscout is invoked with proper arguments
    """
    paramList=sys.argv
    if ("-v" in paramList):
        """
        In addtion the file logging, INFo and above messages will be logged to stdout
        """
        console = logging.StreamHandler()
        console.setLevel(logging.INFO)
        formatter = logging.Formatter('%(levelname)-8s: %(message)s')
        console.setFormatter(formatter)
        logging.getLogger('').addHandler(console)
        logging.info('Screen logging on')
        
    if ("-h" in paramList):
        helpInfo()
        sys.exit() 
        
    if ("-reset" in paramList):
        logging.warning("Resetting database! All data and configuration will be lost!")
        initDB()

    """
        Ensure that the mandatory parameter '-i' or '-r' is specfied
    """ 
    if (not("-i" in paramList or "-r" in paramList)):
        logging.error("\n---ERROR: Either INTERFACE '-i' or REPORT '-r' is MANDATORY---")
        sys.exit()
    
    if("-i" in paramList):
        interfaceInd=paramList.index("-i")+1
        interface=""
        try:
            interface=paramList[interfaceInd]
        except:
            logging.error("\n---ERROR: NO INTERFACE VALUE SPECIFIED---")
            sys.exit()
        logging.info("Netscout: Passive mode")
        utils.setConfigParam("interface", interface)
    else:  
        logging.info("Netscout: Report mode")
        report()
  
def report():
    conn = sqlite3.connect(utils.getCfg('nsDB'))
    conn.close()
    

def initDB():
    """
        Initialize database
    """
    conn = connectDB()
    schemaFile = open(getCfg('nsSchema'));
    conn.executescript(schemaFile.read())
    conn.commit()
    logging.info('Database reset successfully')
    schemaFile.close()
    conn.close()

def netscout():
    """
    Main thread of execution
    """
    logging.basicConfig(filename='netscout.log',format="%(levelname)-8s %(asctime)s \
    Line %(lineno)-5d: %(message)s",level=logging.DEBUG)
    logging.info('==========Initiating netscout logging==========')
    processArgs()
    readConfig()
    createDirStruct()
    #p2p.p2pModel(conn)
    #p2pmodel=p2p.P2PModel(netscout.interface,netscout.P2P_FOLDER)
    #p2pmodel.getHubInfo()
    #p2pmodel.printP2PAnalysis()

"""
Invoke the main thread.
"""
netscout()

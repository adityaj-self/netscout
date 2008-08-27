#!/usr/bin/env python

"""
Author: Aditya Joshi
"""

import sys
import os
import shutil
import logging

import p2p
import utils

def createDirStruct():
    """
    Create the directory struccture for holding network dumps. 
    A directory of the same name (if any) is deleted and recreated.
    """
    try:
        dirstat=os.stat(utils.getCfg('dataDir'))
        shutil.rmtree(utils.getCfg('dataDir'))
    except:
        logging.info('Creating log directories')
    os.mkdir(utils.getCfg('dataDir'))
    os.mkdir(utils.getCfg('p2pDir'))
    os.mkdir(utils.getCfg('httpDir')) 
    
def helpInfo():
    logging.info('nescout version 1.0')
    logging.info('Usage: netscout [-i|-r] <interface> [-reset] ')
    logging.info('Ensure you are root!')

def verInfo():
    logging.info('nescout version 1.0')
    logging.critical('Ensure you are root!')


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
        In addition the file logging, DEBUG and above messages will be logged to stdout
        Edit the Stream logger (second in the handler array to update the logging level)
        """
        logging.getLogger().handlers[1].setLevel(logging.DEBUG)
        logging.info('Detailed Screen logging on')
        
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
        logging.error("Either of INTERFACE '-i' or REPORT '-r' is MANDATORY")
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
        utils.setConfigParam("interface", interface)
    else:  
        logging.info("netscout report mode")
        report()
  
def report():
    conn = utils.connectDB()
    conn.close()
    

def initDB():
    """
        Initialize database
    """
    conn = utils.connectDB()
    schemaFile = open(utils.getCfg('nsSchema'));
    conn.executescript(schemaFile.read())
    conn.commit()
    logging.info('Database reset successfully')
    schemaFile.close()
    conn.close()

def netscout():
    """
    Main thread of execution
    """
    
    """
    Configuring the logging framework
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
    verInfo()
    utils.readConfig()
    processArgs()
    createDirStruct()
    

"""
Invoke the main thread.
"""
netscout()

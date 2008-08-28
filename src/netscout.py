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
        utils.setCfg("interface", interface)
    else:
        if("-i" in paramList):  
            logging.info("netscout report mode")
            report()
        else:
            if("-u" in paramList):
                logging.info("netscout web domain update mode")
                domainUpdate()

def domainUpdate():
    """
    In the mode update the web domains and their category, based on keywords 
    """
    pass

def report():
    conn = utils.connectDB()
    conn.close()


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

def main():
    """
    Main thread of execution
    """
    setupLog()
    verInfo()
    utils.readConfig()
    processArgs()
    createDirStruct()
    if (utils.getCfg("p2pMode") == "true"):
        logging.info("Initialing DC++ P2P scouting")
        p2p.p2pModel()
    
    #httpModel
    #statModel
    
"""
Invoke the main thread.
"""
main()

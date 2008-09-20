import sqlite3
import logging
import ConfigParser
import sys
"""
Utility file
"""

cfg={}

def fileToArray(fileName, validCol):
    """
    Convert file contents given by filename to validCol n-dimensional arrays
    """
    logging.debug("Converting file :"+fileName+" to list data")
    multiList = []
    dataList = []
    for i in range(validCol):
        multiList.append([])
    fileData=open(fileName,'r')
    while 1:
        line = fileData.readline()
        if line:
            line = (line.strip()).split()
            if (len(line) == validCol):
                for i in range(validCol):
                    multiList[i].append(line[i])
        else:
            break
    fileData.close()
    logging.debug("For file : "+fileName+" Data returned: "+str(multiList))
    return multiList


def connectDB():
    """
    Return a connection string to the database
    """
    return sqlite3.connect(getCfg('nsDB'),isolation_level=None)

def getCfg(param):
    """
    Get value ofspecified param
    """
    if (cfg.has_key(param)):
        return cfg[param].strip()
    else:
        logging.error("Parameter :"+param+": not found")
        sys.exit()
    
def setCfg(param, value):
    """
    Set a new param, value pair
    """
    cfg[param]=value

def readConfig():
    """
    Read the config file contents
    """
    logging.info("Reading Configuration Parameters")
    parser = ConfigParser.ConfigParser()
    parser.optionxform = str
    parser.readfp(open('config'))
    for x in parser.sections():
        for y in parser.items(x):
            cfg[y[0]] = y[1]

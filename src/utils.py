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
    Convert file contents given by filename to validCol n-diemnsional arrays
    """
    multiList = []
    dataList = []
    for i in validCol:
        multiList.append(dataList)
    fileData=open(fileName,'r')
    while 1:
        line = fileData.readline()
        if line:
            line = (line.strip()).split()
            if (len(line) == validCol):
                for i in validCol:
                    multiList[i].append(line[i])
        else:
            break
    fileData.close()
    return multiList


def connectDB():
    """
    Return a connection string to the database
    """
    return sqlite3.connect(getCfg('nsDB'))

def getCfg(param):
    """
    Get value ofspecified param
    """
    if (cfg.has_key(param)):
        return cfg[param].strip()
    else:
        logging.error("Parameter "+param+" not found")
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
    parser = ConfigParser.ConfigParser()
    parser.optionxform = str
    parser.readfp(open('config'))
    for x in parser.sections():
        for y in parser.items(x):
            cfg[y[0]] = y[1]

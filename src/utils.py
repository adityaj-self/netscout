import sqlite3
import logging
import ConfigParser
"""
Utility file
"""

cfg={}

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
        return cfg[param]
    else:
        logging.warning("Parameter "+param+" not found")
        return ""
    
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

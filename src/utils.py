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
    if (param in cfg):
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
    parser.readfp(open('config'))
    for x in parser.sections():
        print x
        print parser.options(x)
        print 'hello'
        for y in parser.items(x):
            print y
            cfg[y[0]] = y[1]
    print cfg
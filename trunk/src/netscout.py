#!/usr/bin/env python

import sys
import os
import shutil

import p2p

class netScout:
    def __init__(self):
        print 'Setting log folders'
        self.isNoop=False
        self.msg=""
        self.DATA_FOLDER='netscoutDataLogs'
        self.P2P_FOLDER=self.DATA_FOLDER+'/'+'p2p'
        self.HTTP_FOLDER=self.DATA_FOLDER+'/'+'http'


    def setNoop(self,msg):
        self.isNoop=True
        self.msg=msg
        
    def processArgs(self):
        print 'Processing arguments'
        """
        Scan the input to ensure netscout is invoked with 
        proper arguments
        """
        paramList=sys.argv
    
        """
            For options that do not need any operation set noop and messgae
        """
        if ("-h" in paramList):
            self.setNoop("")
            return 
        
        """
            Ensure that the mandatory parameter '-i' is specfied
        """
        
        if("-i" in paramList):
            interfaceInd=paramList.index("-i")+1
            try:
                interface=paramList[interfaceInd]
            except:
                self.setNoop("\n---ERROR: NO INTERFACE VALUE SPECIFIED---")
                return
            self.datainput="interface"
            self.interface=interface
        else:
            self.setNoop("\n---ERROR: INTERFACE '-i' is MANDATORY---")
            return

    def initFiles(self):
        """
        If directory with the same name as the log folder is found, delete it and recreate
        """
        try:
            dirstat=os.stat(self.DATA_FOLDER)
            shutil.rmtree(self.DATA_FOLDER)
        except:
            print 'Creating log directories'
        os.mkdir(self.DATA_FOLDER)
        os.mkdir(self.HTTP_FOLDER)
        os.mkdir(self.P2P_FOLDER)

    def helpInfo(self):
        print 'nescout version 1.0'
        print 'Usage: netscout -i <interface>'
        print 'Ensure you are root!'
    
    
def passiveAnalysis():
    print 'Starting analysis'
    netscout=netScout()
    netscout.processArgs()
    if (netscout.isNoop):
        print netscout.msg
        netscout.helpInfo()
        sys.exit(0)
    netscout.initFiles()
    print 'Initiating p2p analysis'
    p2pmodel=p2p.P2PModel(netscout.interface,netscout.P2P_FOLDER)
    p2pmodel.getHubInfo()
    p2pmodel.printP2PAnalysis()

passiveAnalysis()

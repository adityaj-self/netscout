import os
import re
import signal

from host import Host

class P2PModel:
    def __init__(self,interface,datafolder):
        print 'Setting up P2P initialization parameters'
        self.interface=interface
        self.datafolder=datafolder
        self.INFO_CNT='10'
        self.INFO_DUMP=self.datafolder+'/'+'myinfo'
        self.HUB_COLS=self.datafolder+'/'+'hub_cols'
        self.HUB_NCOL=2
        self.FILE_CNT='10'
        self.SR_DUMP=self.datafolder+'/'+'searchresult'
        self.SR_COLS=self.datafolder+'/'+'myinfo_cols'
        self.UID_CNT='1'
        self.UID_FILE=self.datafolder+'/'+'uid'
        self.UID_FILE_TSHARK=self.datafolder+'/'+'uid_tshark'
        self.CLT_CNT='2'
        self.CLT_NCOL=1
        self.CLT_FILE=self.datafolder+'/'+'client'
        self.CLT_LDAP_CNT='6'
        self.CLT_LDAP_FILE=self.datafolder+'/'+'client_ldap'
        self.P2P_ANALYSIS=self.datafolder+'/'+'p2p_analysis_results'
	
    def getHubInfo(self):
        print 'Getting HUB info'
        self.identifyP2PHosts()
        self.getHubData()
	
    def fileToHost(self, fileName, validCol):
        fileData=open(fileName,'r')
        thubHostList=[]
        while 1:
            append=False
            line = fileData.readline()
            if not line:
                break
            else:
                line=(line.strip()).split()
                if (len(line) == validCol):
                    append=True
            if(append):
                if(validCol==2):
                    hubHost=Host(line[0],line[1],"Server")
                else:
                    hubHost=Host(line[0],self.hubIP,"Client")
                thubHostList.append(hubHost)
        fileData.close()
        return thubHostList
    
    def identifyP2PHosts(self):
        print 'Identifying P2P Hosts'
        os.system("ngrep -i -q -R -d "+self.interface+" -n "+self.INFO_CNT+" -w MyINFO -O "+self.INFO_DUMP+"> /dev/null")
        print 'Extracting P2P HUB data'
        os.system("ngrep -i -q -R -I "+self.INFO_DUMP+" -w GetNickList -v | grep \"[0-9].[0-9].[0-9].[0-9] [ ->]\" | awk -F\" \" '{print $2}'| awk -F\":\" '{print $1\" \"$2}' | sort -u > "+self.HUB_COLS)
        self.hubHostList=self.fileToHost(self.HUB_COLS,self.HUB_NCOL)
    
    def getHubData(self):
        for i in range(len(self.hubHostList)):
            hostIP=self.hubHostList[i].ipAddr
            print 'Obtaining LDAP IDs: '+hostIP
            print 'Scanning HTTP requests for : '+hostIP
            os.system("touch "+self.UID_FILE_TSHARK)
            os.system("tcpdump -s0 -i "+self.interface+" 'host "+hostIP\
                     +" and tcp dst port 80' -c "+self.UID_CNT+" -w "+self.UID_FILE)
            os.system("tshark -r "+self.UID_FILE+" -T fields -e http.authbasic -R \"http.request && http.authbasic\" | cut -f1 -d ':' > "+self.UID_FILE_TSHARK)
            fuid=open(self.UID_FILE_TSHARK,'r')
            self.hubHostList[i].loginLDAP=fuid.readline()
            fuid.close()
            self.hubHostList[i].p2pActive=True
            self.hubHostList[i].p2pType="Server"
            self.hubHostList[i].fileList=self.getHubFiles(hostIP)
            self.hubHostList[i].clients=self.identifyClients(hostIP,self.hubHostList[i].port)

    def identifyClients(self,hubIP,hostPort):
        print 'Scanning for P2P clients'
        print 'Scanning for P2P clients for HUB: '+hubIP
        self.hubIP=hubIP
        os.system("ngrep -q -i -d "+self.interface+" '' -W byline 'host "+hubIP+" and tcp src port "+hostPort+"' -n "+self.CLT_CNT\
                 +" | grep \"[0-9].[0-9].[0-9].[0-9] [ ->]\" | awk -F\" \" '{print $4}' | awk -F\":\" '{print $1}' |sort -u > "+self.CLT_FILE)
        clientHostList=self.fileToHost(self.CLT_FILE, self.CLT_NCOL)
        print 'Getting LDAP IDs of users acting as P2P Clients'
        for i in range(len(clientHostList)):
            hostIP=clientHostList[i].ipAddr
            print 'Getting LDAP IDs of P2P Client: '+hostIP
            os.system("tcpdump -s0 -i "+self.interface+" 'host "+hostIP\
                     +" and tcp dst port 80' -c "+self.CLT_LDAP_CNT+" -w "+self.CLT_LDAP_FILE)
            os.system("tshark -r "+self.CLT_LDAP_FILE+" -T fields -e http.authbasic -R \"http.request && http.authbasic\" | cut -f1 -d ':' > "+self.UID_FILE_TSHARK)
            fuid=open(self.UID_FILE_TSHARK,'r')
            clientHostList[i].loginLDAP=fuid.readline()
            fuid.close()
            print 'id: '+clientHostList[i].loginLDAP
            clientHostList[i].p2pActive=True
            clientHostList[i].p2pType="Client"
        return clientHostList
    
    def getHubFiles(self,hostIP):
        print 'Getting File List for HUB: '+hostIP
        os.system("ngrep -i -q -R -d "+self.interface+" -W byline -n "+self.FILE_CNT+" -w '\$SR' 'src host "+hostIP+"' > "+self.SR_DUMP)
        allFileData = open(self.SR_DUMP,'r').read()
        p=re.compile('\|\$SR [0-9A-Z_]*', re.DOTALL | re.IGNORECASE)
        q=re.compile('[0-9]/[0-9]\.TTH:[0-9A-Z]*', re.DOTALL | re.IGNORECASE)
        markstart=p.sub(' FILESTART',allFileData)
        markend=q.sub(' FILEEND',markstart)
        fileList=re.findall('FILESTART.*?FILEEND', markend, re.DOTALL | re.IGNORECASE)
        print '\n ---------------------------------------------------\n'
        print '\tSearching for video files hosted by HUB: '+hostIP+'\n'
        print '\n ---------------------------------------------------\n'
        i=0
        for j in range(len(fileList)):
             fromInd=fileList[j].rfind('\\')
             fileList[j]=fileList[j].lower()
             fromInd=fromInd+1
             toInd=0
             if ('.avi' in fileList[j]):
                 toInd=fileList[j].rfind('.avi')
                 toInd=toInd+4
             elif ('.mpeg' in fileList[j]):
                 toInd=fileList[j].upper().rfind('.mpeg')    
                 toInd=toInd+5                 
             elif ('.mpg' in fileList[j]):
                 toInd=fileList[j].rfind('.mpg')    
                 toInd=toInd+4                 
             elif ('.wmv' in fileList[j]):
                 toInd=fileList[j].rfind('.wmv')    
                 toInd=toInd+4
             elif ('.mov' in fileList[j]):
                 toInd=fileList[j].rfind('.mov')    
                 toInd=toInd+4
             elif ('.mov' in fileList[j]):
                 toInd=fileList[j].rfind('.rm')    
                 toInd=toInd+3
            
             if (fileList[j][fromInd:toInd].strip()!='' and toInd!=0):
                 i=i+1
                 print i,') ',fileList[j][fromInd:toInd]
        return fileList


    def printP2PAnalysis(self):
        hubs=self.hubHostList
        print 'P2P Analysis'
        print '------------'
        os.system("touch "+self.P2P_ANALYSIS) 
        #p2pOutput=open(self.P2P_ANALYSIS,'r+')
        for i in range(len(hubs)):
            clients=hubs[i].clients
            #p2pOuptput.write()
            print 'HUB IP'.rjust(16)+'PORT'.rjust(6)+'LDAP ID'.rjust(10)
            print hubs[i].ipAddr.rjust(16)+hubs[i].port.rjust(6)+hubs[i].loginLDAP.rjust(10)
            print 'Clients connected to the HUB'
            for i in range(len(clients)):
                print 'Client IP'.rjust(16)+'LDAP ID'.rjust(10)
                print clients[i].ipAddr.rjust(16)+clients[i].loginLDAP.rjust(10)
        #p2pOuptput.close()

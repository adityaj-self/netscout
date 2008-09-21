import logging
import os
import utils

def categoriseWeb():
    pass
    
def getWebActivity(hostIP):
    cmd = "tcpdump -i "+utils.getCfg('interface')
    cmd +=" src host "+hostIP+" -n "+utils.getCfg('singleWebCnt')
    if(utils.getCfg('proxy') == "true"):
        cmd +=" and dst host "+utils.getCfg('proxyHost')
    cmd+=" -w "+utils.getCfg('webActFile')
    os.system(cmd)
    
def viaProxy():
    pass

def httpActivity():
    cmd = "tcpdump -i "+utils.getCfg('interface')+" -n "+utils.getCfg('multiWebCnt')
    if(utils.getCfg('proxy') == "true"):
        cmd +=" dst host "+utils.getCfg('proxyHost')
    cmd+=" -w "+utils.getCfg('webActFile')
    os.system(cmd)
    
    
def domainUpdate():
    """
    In the mode update the web domains and their category, based on keywords 
    """
    domainList=[]
    conn=utils.connectDB()
    cur = conn.cursor();
    p=-1
    urlList = ""
    if(utils.getCfg("update") == "all"):
        cur.execute("select * from webdomain");
    else:
        cur.execute("select * from webdomain where catID = ?",p);
    domainList = cur.fetchmany()[1]
    for i in domainList:
        urlList = urlList + " "+i
    if(urlList != ""):
        os.system("wget -xq --level=1 --tries=1 "+urlList)
        
    else:
        logging.info("No new websites to identify")
    
    conn.close()

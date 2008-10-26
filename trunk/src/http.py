## Author - Aditya Joshi
## File - http.py

import logging
import os

import utils
import const

dbDomains={} #domains in the db
categories={}

def getDomainInfo():
    conn = utils.connectDB()
    cur = conn.cursor()
    cur.execute("select * from webdomain")
    domainData = cur.fetchall()
    logging.debug("Found existing "+str(len(domainData))+" domains")
    for i in range(len(domainData)):
        dbDomains[domainData[i][const.NAME_IND]] = domainData[i][const.ID_IND]
    conn.close()
    return dbDomains

def addHttpAct(hostActID,domainID):
    t = (hostActID,domainID)
    conn = utils.connectDB()
    cur = conn.cursor()
    cur.execute("insert into httpAct(hostActID,domainID) values (?,?) ",t)
    conn.close()

def categoriseUrl(url):
    os.system("sed -n -e '/<head>/,/<\/head>/p' <"+\
		    +getCfg("httpDir")+"/"+url+" | sed -n -e '/<meta/,/>/p' >"+url)
    fp=open("url")
    metaData = fp.read()
    for (cat,keyword) in config.category.items():
	for word in keyword:
	    if word in metaData:
		
		break
		 


    
def extractDomains(hostIP):
    webFile = open(utils.getCfg("webActFile")) 
    os.system("tcpdump -s0 -i "+utils.getCfg("interface")+" 'host "+hostIP\
             +" and tcp dst port 80' -c "+getCfg("singleWebCnt")+" -w - | "\
             +" tshark -i - -T fields -e http.host -R \"http.host\" | sort -u > "\
	     +getCfg("webActHostFile"))
    return utils.fileToArray(getCfg("webActHostFile"))[0];


def viaProxy():
    pass

def httpActivity():
    """
    Intiating http activity
    """
    getDomainInfo() 
    # First get http activity of hosts found (if any) during previous analysis
    for (id,ip) in host.dbHosts.items():
	getWebActivity(ip)
	domainVisited=extractDomains(v)
	webDomains = dbDomains.keys()
	for dV in domainVisited:
	    if (dv in webDomains):
		domID = webDomains.get(dV)
		if(domID == None):
		    domID = const.UNCLASSED 
		addHttpAct(addHostActivity(ip,host.sessionUsers[value]),domID)
    
def domainUpdate():
    """
    In the mode update the web domains and their category, based on keywords 
    """
    domainList=[]
    conn=utils.connectDB()
    cur = conn.cursor();
    p=const.UNCLASSED
    urlList = ""
    if(utils.getCfg("update") == "all"):
        cur.execute("select * from webdomain");
    else:
        cur.execute("select * from webdomain where catID = ?",p);
    domainList = cur.fetchall()
    for i in range(len(domainList)):
        url = domainList[i][const.NAME_IND]
	if(url != ""):
	    os.system("wget --quiet --level=1 --output-document="\
			    +getCfg("httpDir")+"/"+url+" --tries=1 "+url)
	    categoriseSite(url)
    conn.close()
    logging.info(str(len(domainList))+" sites categoried/updated")

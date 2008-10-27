## Author - Aditya Joshi
## File - http.py

import logging
import os

import utils
import const
import host

dbDomains={} #domains in the db
dbCategories={} #categories and their ids

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

def extractDomains(hostIP):
    os.system("tshark -i "+utils.getCfg("interface")+" -c "+utils.getCfg("singleWebCnt")\
		+" -T fields -e http.host -R \"http.host && ip.src=="+hostIP+"\""\
		+" | sort -u > "+utils.getCfg("webActHostFile"))
    return utils.fileToArray(utils.getCfg("webActHostFile"),1)[0];

def addNewDomain(domain):
    conn = utils.connectDB()
    cur = conn.cursor()
    t = (domain,const.UNCLASSED,)
    cur.execute("insert into webdomain(domain,category) values (?,?)",t)
    cur.execute("select max(domainID) from webdomain")
    maxID = int(cur.fetchone()[0])
    dbDomains[maxID] = domain
    conn.close()
    return maxID



def httpActivity():
    """
    Intiating http activity
    """
    getDomainInfo()
    # First get http activity of hosts found (if any) during previous analysis
    for (id,ip) in host.dbHosts.items():
	userid=host.extractUserID(ip)
	domainVisited=extractDomains(ip)
	webDomains = dbDomains.keys()
	hostActID  = host.addHostActivity(ip,userid)[const.HA_ID]
	for dv in domainVisited:
	    if (dv in webDomains):
		domID = webDomains.get(dv)
	    else:
		domID = addNewDomain(dv)
	    addHttpAct(hostActID,domID)



def domainUpdate():
    """
    In the mode update the web domains and their category, based on keywords 
    """
    domainList=[]
    conn=utils.connectDB()
    cur = conn.cursor()
    p=const.UNCLASSED
    urlList = ""
    addCategorytoDB()
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
	    newCat = categoriseSite(url)
	    ## Update category in DB
	    t=(newCat,domainList[i][const.ID_IND],)
	    cur.execute("update webdomain set category = ? where domainID = ?",t) 
    conn.close()
    logging.info(str(len(domainList))+" sites categoried/updated")

def categoriseUrl(url):
    os.system("sed -n -e '/<head>/,/<\/head>/p' <"+\
		    +getCfg("httpDir")+"/"+url+" | sed -n -e '/<meta/,/>/p' >"+url)
    fp=open("url")
    metaData = fp.read()
    for (cat,keyword) in config.category.items():
	for word in keyword:
	    if word in metaData:
		return cat	
    return ""



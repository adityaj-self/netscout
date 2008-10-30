## Author - Aditya Joshi
## File - http.py

import logging
import os

import utils
import const
import host

dbDomains={} #domains in the db

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
    p=(const.UNCLASSED,)
    urlList = ""
    if(utils.getCfg("update") == "all"):
        cur.execute("select * from webdomain");
    else:
        cur.execute("select * from webdomain where category = ?",p);
    categories = utils.getCategories()
    domainList = cur.fetchall()
    for i in range(len(domainList)):
        url = domainList[i][const.NAME_IND]
	if(url != ""):
	    os.system("wget --quiet --level=1 --output-document="\
			+utils.getCfg("httpDir")+"/"+url+" --tries=1 "+url)
	    newCat = categoriseUrl(url,categories)
	    ## Update category in DB
	    t=(newCat,domainList[i][const.ID_IND],)
	    logging.debug("t:"+str(t))
	    cur.execute("update webdomain set category = ? where domainID = ?",t) 
    conn.close()
    logging.info(str(len(domainList))+" sites categoried/updated")

def categoriseUrl(url,categories):
    logging.debug("Categorising: "+url)
    urlLoc = utils.getCfg("httpDir")+"/"+url
    os.system("sed -n -e '/<head>/,/<\/head>/p' <"\
		    +urlLoc+" | sed -n -e '/<meta/,/>/p' >"\
		    +urlLoc+".sed")
    fp=open(urlLoc)
    metaData = fp.read()
    for (cat,key) in categories.items():
	logging.debug("cat: "+cat+" keywords: "+str(key))
	for word in key:
	    logging.debug("in word:"+str(word))
	    if word in metaData:
		logging.debug("found word:"+str(word)+": returning cat: "+str(cat))
		return cat	
    return const.UNCLASSED


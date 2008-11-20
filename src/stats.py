"""
Statistical analysis
"""
import logging

import utils
import const
import host

def statActivity():
    logging.debug("starting statistical mode")
    #look for number of connections into
    #look for bandwidth usage
    #look for number of requests to specific hosts
    os.system("tcpdump -s0 -i "+getCfg("interface")\
		+" 'dst not "+getCfg("ignoreHost")\+"'"\
		+" -c "+getCfg("connTo")+" -w - | "\
		+" tshark -i - -T fields -e ip.dst |"\
		+" sort > "+getCfg("dstCountFile"))
    dstList = utils.fileToArray(getCfg("dstCountFile"))
    uniqueDst = list(set(dstList))
    highDstConn = []
    for ip in uniqueDst:
	if dstList.count(ip) >= int(getCfg("connToMin")):
	    highDstConn.append(ip)
    host.addHostActivity(ip,extractUserID(ip)) 


def protectResource():
    logging.debug("starting protection mode")
    #look for number of connections into
    #look for bandwidth usage
    #look for number of requests to specific hosts
    os.system("tcpdump -s0 -i "+getCfg("interface")\
		+" 'dst  "+getCfg("impRes")\+"'"\
		+" -c "+getCfg("prConnTo")+" -w - | "\
		+" tshark -i - -T fields -e ip.src |"\
		+" sort > "+getCfg("srcCountFile"))
    srcList = utils.fileToArray(getCfg("srcCountFile"))
    uniqueSrc = list(set(srcList))
    highSrcConn = []
    for ip in uniqueSrc:
	if srcList.count(ip) >= int(getCfg("prConnToMin")):
	    highSrcConn.append(ip)
    host.addHostActivity(ip,extractUserID(ip)) 
    



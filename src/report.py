"""
Generating reports for netscout
"""

import logging
import sys

import utils
import host
import const
import time


def overview():
    conn = utils.connectDB()
    cur = conn.cursor()
    logging.debug("reporting findings")
    hosts = host.getHostsFromDB()
    users = host.getUsersFromDB()
    logging.debug("len(hosts):"+str(len(hosts)))
    if (len(hosts) == 0):
	logging.info("No data available to generate report")
	sys.exit()
    for hostID,hostIP in hosts.items():
        print'\n------------------------------------------------------'
        print'------------------------------------------------------'
        print'\nHOST:'+hostIP
        t = (hostID,)
        cur.execute('select * from hostAct where hostID = ?', t)
        rs = cur.fetchall()
        for i in range(len(rs)):
            print'\t Activity: '+str(i)
            print'\t User ID : '+users[rs[i][const.HA_USER_ID]].strip()
            print'\t Time    : '+time.asctime(time.localtime(int(rs[i][const.HA_TIME])))
            t = (rs[i][const.HA_ID],)
            cur.execute('select * from p2pAct where hostActID = ?', t)
            rs1 = cur.fetchall()
            for j in range(len(rs1)):
                print'\t\t P2P Act : '+str(j)
                if (rs1[j][const.P2P_HUBTYPE] == const.SERVER):
                    print'\t\t P2P Type: SERVER'
                    print'\t\t PORT    : '+str(rs1[j][const.P2P_PORT_HUBID])
		    cur.execute('select * from fileList where hostActID = ?',t)
		    rs2 = cur.fetchall()
		    print'\t\t FILES: \n'+str(rs2[const.ROW_ID][const.FILELIST_ID])
                else:
                    print'\t\t P2P Type: CLIENT'
                    print'\t\t SERVER  : '+str(host.getHostNameByID(rs1[j][const.P2P_PORT_HUBID]))
    sys.exit()


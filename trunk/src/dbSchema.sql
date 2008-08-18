-- SQLite3 schema file for the netscout project

CREATE TABLE IF NOT EXISTS netscout.host
(
    hostID INTEGER PRIMARY KEY AUTOINCREMENT,
    hostIP TEXT
)


CREATE TABLE IF NOT EXISTS netscout.ldap
(
    ldapID INTEGER PRIMARY KEY AUTOINCREMENT,
    ldapUser TEXT
)

CREATE TABLE IF NOT EXISTS netscout.hostAct
(
    hostActID INTEGER PRIMARY KEY AUTOINCREMENT,
    --seconds from EPOCH
    timestamp INTEGER,
    hostID INTEGER,
    ldapID INTEGER,
    hwAddr TEXT    
)

CREATE TABLE IF NOT EXISTS netscout.httpAct
(
    httpActID INTEGER PRIMARY KEY AUTOINCREMENT,
    hostActID INTEGER,
    domainID INTEGER
)

CREATE TABLE IF NOT EXISTS netscout.p2pAct
(
    p2pActID INTEGER PRIMARY KEY AUTOINCREMENT,
    hostActID INTEGER,
    domainID INTEGER
    hubType TEXT, -- Server or Client
    serverID INTEGER -- ID of Server (host ID), if server then link to fileList
)

CREATE TABLE IF NOT EXISTS netscout.fileList
(
    fileListID INTEGER PRIMARY KEY AUTOINCREMENT,
    fileType TEXT, -- Video, Audio
    fileList TEXT -- List of particular type
)


CREATE TABLE IF NOT EXISTS netscout.webdomain
(
    domainID INTEGER PRIMARY KEY AUTOINCREMENT,
    domain TEXT,
    catID INTEGER,
)

CREATE TABLE IF NOT EXISTS netscout.domainCat
(
    catID INTEGER PRIMARY KEY AUTOINCREMENT,
    catName TEXT,
    blacklist BOOLEAN,
    keywords TEXT
)



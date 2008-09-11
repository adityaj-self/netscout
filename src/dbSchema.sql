-- SQLite3 schema file for the netscout project

CREATE TABLE IF NOT EXISTS host 
(   hostID INTEGER PRIMARY KEY AUTOINCREMENT,
    hostIP TEXT
);


CREATE TABLE IF NOT EXISTS user
(   userID INTEGER PRIMARY KEY AUTOINCREMENT,
    userName TEXT
);

CREATE TABLE IF NOT EXISTS hostAct
(
    hostActID INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp INTEGER, --seconds from EPOCH
    hostID INTEGER,
    userID INTEGER,
    hwAddr TEXT    
);

CREATE TABLE IF NOT EXISTS httpAct
(
    httpActID INTEGER PRIMARY KEY AUTOINCREMENT,
    hostActID INTEGER,
    domainID INTEGER
);

CREATE TABLE IF NOT EXISTS p2pAct
(
    p2pActID INTEGER PRIMARY KEY AUTOINCREMENT,
    hostActID INTEGER,
    hubType INTEGER, -- 0-Server or 1-Client
    portNumOrHubIP INTEGER, -- Server Port or ID of Server (host ID) if client 
);

CREATE TABLE IF NOT EXISTS fileList
(
    hostActID INTEGER
    fileList TEXT -- List of particular type
);


CREATE TABLE IF NOT EXISTS webdomain
(
    domainID INTEGER PRIMARY KEY AUTOINCREMENT,
    domain TEXT,
    catID INTEGER
);

CREATE TABLE IF NOT EXISTS domainCat
(
    catID INTEGER PRIMARY KEY AUTOINCREMENT,
    catName TEXT,
    blacklist BOOLEAN,
    keywords TEXT
);


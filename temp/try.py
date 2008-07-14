from ConfigParser import ConfigParser

print 'config test'
configObj=ConfigParser()
configObj.readfp(open('tryconf'))
print configObj.sections()
print configObj.options('P2P')
configObj.set('P2P','DATA_FOLDER','hello')
print configObj.get('P2P','DATA_FOLDER')
print configObj.get('P2P','UID_FILE')

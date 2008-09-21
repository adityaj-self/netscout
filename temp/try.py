import sqlite3
import ConfigParser

cfg = {}

parser = ConfigParser.ConfigParser()
parser.optionxform = str
parser.readfp(open('../src/config'))
for x in parser.sections():
    for y in parser.items(x):
        cfg[y[0]] = y[1]
l = []
l = cfg['ext'].split(',')
print l
for m in l:
    print m
    
p = ['abc','245']

for m in p:
    print m

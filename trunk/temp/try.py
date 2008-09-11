import sqlite3

import utils

conn = sqlite3.connect('testdb')
cur = conn.cursor()
cur.execute("select * from temp")
print  cur.fetchone()[2]

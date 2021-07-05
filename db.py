import sqlite3

conn = sqlite3.connect('prospects.db')
c = conn.cursor()
#c.execute('''CREATE TABLE prospects('''site TEXT,  '''))
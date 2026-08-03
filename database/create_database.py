import sqlite3


conn = sqlite3.connect("database/job_copilot.db")

cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS jobs(

id INTEGER PRIMARY KEY AUTOINCREMENT,

title TEXT,

company TEXT,

location TEXT,

source TEXT,

url TEXT,

skills TEXT,

salary TEXT,

posted_date TEXT

)
""")

conn.commit()

conn.close()

print("Database Created Successfully")
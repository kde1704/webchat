import sqlite3
import atexit

def init(db_p):
    global db
    db = db_p

def execute(cmd, args):
    with sqlite3.connect(db) as conn:
        c = conn.cursor()
        c.execute("PRAGMA foreign_keys = 1")
        c.execute(cmd, args)
        r = c.fetchall()
        if r:
            return r
        else:
            conn.commit()
            return None

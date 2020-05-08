import sqlite3


def init_sql():
    conn = sqlite3.connect("db.fps")
    c = conn.cursor()
    print "Open database successfully"
    c.execute('''
        CREATE TABLE IF NOT EXISTS `user`  (
        `user_id` INTEGER PRIMARY KEY AUTOINCREMENT,
        `user_name` MESSAGE_TEXT NULL,
        `user_pwd` MESSAGE_TEXT NULL,
        `user_room` INTEGER NULL);''')
    print "Init successfully"


def select(s, v):
    conn = sqlite3.connect("db.fps")
    try:
        c = conn.cursor()
        print "Open database successfully"
        cursor = c.execute(s, v)
        return cursor.rowcount
    finally:
        conn.close()


def select_keep_connect(s, v):
    conn = sqlite3.connect("db.fps")
    c = conn.cursor()
    cursor = c.execute(s, v)
    return conn, cursor


def insert(s, v):
    conn = sqlite3.connect("db.fps")
    try:
        c = conn.cursor()
        print "Open database successfully"
        c.execute(s, v)
        conn.commit()
        print "Commit successfully"
    finally:
        conn.close()

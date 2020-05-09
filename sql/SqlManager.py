import sqlite3


def init_sql():
    conn = sqlite3.connect("db.fps")
    try:
        c = conn.cursor()
        c.execute('''
            CREATE TABLE IF NOT EXISTS `user`  (
            `user_id` INTEGER PRIMARY KEY AUTOINCREMENT,
            `user_name` MESSAGE_TEXT NULL,
            `user_pwd` MESSAGE_TEXT NULL,
            `user_room` INTEGER NULL);''')
    finally:
        conn.close()
    print "Init successfully"


def select(s, v):
    conn = sqlite3.connect("db.fps")
    try:
        c = conn.cursor()
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
        c.execute(s, v)
        conn.commit()
    finally:
        conn.close()

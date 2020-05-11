import sqlite3

sql_name = 'db.fps'


def init_sql():
    conn = sqlite3.connect(sql_name)
    try:
        c = conn.cursor()
        c.execute('''
            CREATE TABLE IF NOT EXISTS `user`  (
            `user_id` INTEGER PRIMARY KEY AUTOINCREMENT,
            `user_name` MESSAGE_TEXT NULL,
            `user_pwd` MESSAGE_TEXT NULL,
            `user_room` INTEGER NULL);''')

        print "all:"
        cursor = c.execute('''select * from user''')
        for row in cursor:
            print row

    except Exception as e:
        print e
    finally:
        conn.close()
    print "Init successfully"


def connect_sql():
    conn = sqlite3.connect(sql_name)
    c = conn.cursor()
    return conn, c

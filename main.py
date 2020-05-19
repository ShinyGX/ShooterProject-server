# encoding=utf-8

import network
import sql

if __name__ == "__main__":

    sql.SqlManager.init_sql()
    server = network.BattleTcpServer("127.0.0.1", 9999)
    server.start_session()

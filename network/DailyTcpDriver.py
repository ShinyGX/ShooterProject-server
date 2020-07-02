# coding=utf-8
import json
import threading
from socket import *

from core import BattleRoomHandler
from core import Singleton
from network import BattleTcpServer
from sql import SqlManager

from network.NetworkInputStream import NetworkInputStream
from network.NetworkOutputStream import NetworkOutputStream


class DailyTcpServer(object):
    __socket = socket(AF_INET, SOCK_STREAM)
    __address = ('', 4396)
    __buf = 1024

    def __init__(self):
        self.__socket.bind(self.__address)
        self.__socket.listen(5)

    def start_session(self):
        try:
            print "Waiting Players"
            while True:
                cs, addr = self.__socket.accept()
                print "Player[%s:%s] join in" % (addr[0], addr[1])
                start_thread(cs, addr)

        except error as e:
            print e
            pass


class DailyThread(threading.Thread):
    __buf = 1024

    def __init__(self, cs, addr):
        super(DailyThread, self).__init__()
        self.__cs = cs
        self.__addr = addr
        self.__handler = DailyHandle()

    def run(self):
        try:
            while True:
                data = self.__cs.recv(self.__buf)
                if not data:
                    break
                self.__handler.handle_msg(self.__cs, data)
        except error as e:
            print e
            pass
        finally:
            self.__cs.close()


def start_thread(cs, addr):
    thread = DailyThread(cs, addr)
    thread.start()


class DailyHandle(Singleton):
    __output_stream = NetworkOutputStream()
    __input_stream = NetworkInputStream(None)

    __ip = "127.0.0.1"
    __port = 9824

    __free_server = []
    __running_server = []

    __battle_room_handler = BattleRoomHandler()

    __mutex = threading.Lock()

    def handle_msg(self, cs, data):
        self.__mutex.acquire()

        self.__input_stream.reset_stream(data)
        js = json.loads(self.__input_stream.get_data_bytes())
        conn, c = SqlManager.connect_sql()
        if js["type"] == "login":
            username = js["username"]
            pwd = js["pwd"]
            cursor = c.execute("select * from user where user_name=? and user_pwd=?", (username, pwd))
            size = len(cursor.fetchall())

            self.__output_stream.push_char(1)
            if size > 0:
                self.__output_stream.push_string(
                    json.dumps(
                        {
                            "type": "login",
                            "msg": username,
                            "data": True
                        }
                    ))
                cs.sendall(self.__output_stream.flush_stream())
            else:
                self.__output_stream.push_string(
                    json.dumps(
                        {
                            "type": "login",
                            "msg": "account not found",
                            "data": False
                        }
                    ))
                cs.sendall(self.__output_stream.flush_stream())
        elif js["type"] == "register":
            username = js["username"]
            pwd = js["pwd"]

            cursor = c.execute('''select * from where user_name=?''', (username,))
            exist_account = len(cursor.fetchall())

            self.__output_stream.push_char(2)
            if exist_account > 0:
                self.__output_stream.push_string(
                    json.dumps(
                        {
                            "type": "register",
                            "msg": "account exist",
                            "data": False
                        }))
                cs.sendall(self.__output_stream.flush_stream())
            else:
                c.execute(
                    '''insert into user (user_name,user_pwd) values(?,?)''',
                    (username, pwd))
                conn.commit()

                self.__output_stream.push_string(
                    json.dumps(
                        {
                            "type": "register",
                            "msg": username,
                            "data": True
                        }))
                cs.sendall(self.__output_stream.flush_stream())
        elif js["type"] == "match":
            name = js["name"]
            room, client_id = self.__battle_room_handler.get_room(name, cs)
            self.__output_stream.push_char(3)
            self.__output_stream.push_string(
                json.dumps(
                    {
                        "roomId": room.room_id,
                        "clientId": client_id
                    }))
            cs.sendall(self.__output_stream.flush_stream())

            if self.__battle_room_handler.is_full(room.room_id):
                print "room full", room.room_id, client_id
                self.__output_stream.push_char(6)
                self.__output_stream.push_string(
                    json.dumps({
                        "msg": "matched"
                    }))
                room.broadcast(self.__output_stream.flush_stream())
        elif js["type"] == "ready":
            client_id = js["clientId"]
            room_id = js["roomId"]
            ret = self.__battle_room_handler.ready(room_id, client_id)
            print "ready ", room_id, client_id
            if not ret:
                self.__output_stream.push_char(4)
                self.__output_stream.push_string(
                    json.dumps({
                        "error": "Room Not Found"
                    }))
                cs.sendall(self.__output_stream.flush_stream())

            # If All Ready,Start Game
            if self.__battle_room_handler.is_all_ready(room_id):
                server = self.__get_server()
                addr = server.get_bind_addr()
                self.__output_stream.push_char(5)
                self.__output_stream.push_string(
                    json.dumps({
                        "ip": addr[0],
                        "port": addr[1]
                    }))
                self.__battle_room_handler.broadcast_room(room_id, self.__output_stream.flush_stream())

        else:
            self.__output_stream.push_string(
                json.dumps(
                    {
                        "type": "unknown",
                        "msg": "unknown type",
                        "data": False
                    }))
            cs.sendall(self.__output_stream.flush_stream())

        conn.close()
        self.__mutex.release()

    def __get_server(self):
        if len(self.__free_server) > 0:
            server = self.__free_server.pop()
            self.__running_server.append(server)
        else:
            server = BattleTcpServer(self.__ip, self.__port)
            self.__port += 1
            self.__running_server.append(server)

        return server

# coding=utf-8
import json
import struct
import threading
from socket import *

from network.Protocol import NetworkProtocol
from sql import SqlManager


class DailyTcpServer(object):
    __socket = socket(AF_INET, SOCK_STREAM)
    __address = ('', 4396)
    __buf = 1024

    def __init__(self):
        self.__socket.bind(self.__address)
        self.__socket.listen(5)

    def start_session(self):
        try:
            print "等待玩家"
            while True:
                cs, addr = self.__socket.accept()
                print "接收到 %s:%s的玩家" % (addr[0], addr[1])
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


class DailyHandle(object):
    __protocol = NetworkProtocol()

    def handle_msg(self, cs, data):

        data_size = struct.unpack("<i", data[:4])
        print data_size
        js = json.loads(data[4:])
        print js
        if js["type"] == "login":
            username = js["username"]
            pwd = js["pwd"]
            size = SqlManager.select(
                '''select * from user where user_name=? and user_pwd=?''',
                (username, pwd))
            if size > 0:
                self.__protocol.push_string(
                    json.dumps(
                        {
                            "code": 200,
                            "msg": "login success",
                            "data": True
                        }
                    ))
                cs.sendall(self.__protocol.flush_data())
            else:
                self.__protocol.push_string(
                    json.dumps(
                        {
                            "code": 199,
                            "msg": "account not found",
                            "data": False
                        }
                    ))
                cs.sendall(self.__protocol.flush_data())
        elif js["type"] == "register":
            username = js["username"]
            pwd = js["pwd"]
            SqlManager.insert(
                '''insert into user (user_name,user_pwd) value(?,?)''',
                (username, pwd))

            self.__protocol.push_string(
                json.dumps(
                    {
                        "code": 200,
                        "msg": "register success",
                        "data": True
                    }))
            cs.sendall(self.__protocol.flush_data())
        else:
            self.__protocol.push_string(
                json.dumps(
                    {
                        "code": 1998,
                        "msg": "unknown type",
                        "data": False
                    }))
            cs.sendall(self.__protocol.flush_data())

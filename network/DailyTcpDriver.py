# coding=utf-8
import json
import struct
import threading
from socket import *

from network.NetworkInputStream import NetworkInputStream
from network.NetworkOutputStream import NetworkOutputStream
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
    __output_stream = NetworkOutputStream()
    __input_stream = NetworkInputStream()

    def handle_msg(self, cs, data):
        self.__input_stream.reset_stream(data)
        data_size = self.__input_stream.get_data_len()
        print data_size
        js = json.loads(self.__input_stream.get_data_bytes())
        print js
        if js["type"] == "login":
            username = js["username"]
            pwd = js["pwd"]
            size = SqlManager.select(
                '''select * from user where user_name=? and user_pwd=?''',
                (username, pwd))
            if size > 0:
                self.__output_stream.push_string(
                    json.dumps(
                        {
                            "code": 200,
                            "msg": "login success",
                            "data": True
                        }
                    ))
                cs.sendall(self.__output_stream.flush_stream())
            else:
                self.__output_stream.push_string(
                    json.dumps(
                        {
                            "code": 199,
                            "msg": "account not found",
                            "data": False
                        }
                    ))
                cs.sendall(self.__output_stream.flush_stream())
        elif js["type"] == "register":
            username = js["username"]
            pwd = js["pwd"]
            SqlManager.insert(
                '''insert into user (user_name,user_pwd) value(?,?)''',
                (username, pwd))

            self.__output_stream.push_string(
                json.dumps(
                    {
                        "code": 200,
                        "msg": "register success",
                        "data": True
                    }))
            cs.sendall(self.__output_stream.flush_stream())
        else:
            self.__output_stream.push_string(
                json.dumps(
                    {
                        "code": 1998,
                        "msg": "unknown type",
                        "data": False
                    }))
            cs.sendall(self.__output_stream.flush_stream())

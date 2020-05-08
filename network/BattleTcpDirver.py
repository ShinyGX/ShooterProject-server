# coding=utf-8
from socket import *
import threading
import struct

from network.NetworkOutputStream import NetworkOutputStream


class BattleTcpServer(object):
    __socket = socket(AF_INET, SOCK_STREAM)
    __address = ('', 9963)
    __buf = 1024

    def __init__(self):
        self.__socket.bind(self.__address)
        self.__socket.listen(5)
        self.__msg_handler = BattleHandler()

    def start_session(self):
        try:
            print "等待玩家"
            while True:
                cs, addr = self.__socket.accept()
                print "接收到 %s:%s的玩家" % (addr[0], addr[1])
                self.__msg_handler.start_thead(cs, addr)

        except error as e:
            print e
            pass


class BattleThread(threading.Thread):
    __buf = 1024

    __end_mask = struct.pack("c", chr(255))
    __init_mask = struct.pack("c", chr(1))

    def __init__(self, cs, addr, msg_handler):
        super(BattleThread, self).__init__()
        self.__cs = cs
        self.__addr = addr
        self.__msg_handler = msg_handler

    def run(self):
        try:
            self.__msg_handler.init_room(self.__cs)
            while True:
                data = self.__cs.recv(self.__buf)
                if not data:
                    break
                self.__msg_handler.handle_msg(self.__cs, data)
        except error as e:
            print e
            pass
        finally:
            self.__msg_handler.close_connect(self.__cs)
            self.__cs.close()


class BattleHandler(object):
    __buf = 1024
    __socket_list = []
    __step_message = []
    __room_list = []

    __protocol = NetworkOutputStream()
    __mutex = threading.Lock()

    def handle_msg(self, cs, data):
        self.__socket_list.append(cs)
        code = struct.unpack("I", data)
        if code == 1:
            cs.sendall(struct.pack("i", 2))
        else:
            cs.sendall(data)

    def start_thead(self, cs, addr):
        self.__socket_list.append(cs)
        battle_thread = BattleThread(cs, addr, self)
        battle_thread.start()

    def init_room(self, cs):
        self.__protocol.push_char(1)
        cs.sendall(self.__protocol.flush_stream())

    def close_connect(self, cs):
        if self.__mutex.acquire():
            try:
                if cs in self.__socket_list:
                    print "%s离开了" % cs
                    self.__socket_list.remove(cs)
            finally:
                self.__mutex.release()

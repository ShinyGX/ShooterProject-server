# coding=utf-8

from socket import *
import threading
import random
from time import sleep

from enum import Enum, unique

from Log.ConsoleLog import ConsoleLog
from network.IndexObjectPool import IndexObjectPool
from network.NetworkInputStream import NetworkInputStream
from network.NetworkOutputStream import NetworkOutputStream


class BattleTcpServer(object):
    __socket = socket(AF_INET, SOCK_STREAM)
    __buf = 1024

    def __init__(self, ip, port):
        self.__address = (ip, port)
        self.__socket.bind(self.__address)
        self.__socket.listen(5)
        self.__msg_handler = BattleHandler(5)
        self.__port = port
        self.__addr = ip

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

    def get_bind_addr(self):
        return self.__addr, self.__port


class BattleThread(threading.Thread):
    __active = 30
    __buf = 1024

    __client_id = -1

    def __init__(self, cs, addr, msg_handler):
        super(BattleThread, self).__init__()
        self.__cs = cs
        self.__addr = addr
        self.__msg_handler = msg_handler

    def set_client_id(self, client_id):
        self.__client_id = client_id

    def send(self, data):
        self.__cs.sendall(data)

    def run(self):
        try:
            self.__msg_handler.init_room(self)
            while True:
                data = self.__cs.recv(self.__buf)
                if not data:
                    break
                self.__msg_handler.handle_msg(self.__client_id, data)
        except error as e:
            print e
            pass
        finally:
            self.close()

    def close(self):
        self.__msg_handler.close_connect(self.__client_id)
        self.__cs.close()

    def set_active(self):
        self.__active = 30

    def check_active(self):
        self.__active -= 1
        return self.__active >= 0

    def get_addr(self):
        return self.__addr[0]

    def get_client_id(self):
        return self.__client_id


class BattleSyncServer(threading.Thread):

    def __init__(self, handler):
        super(BattleSyncServer, self).__init__()
        self.__handler = handler
        self.__running = True

    def run(self):
        while self.__running:
            self.__handler.send_all_player()
            sleep(0.066)

    def set_run(self, value):
        self.__running = value


class BattleHandler(object):
    __buf = 1024
    __step_message = []

    __frame = []

    __protocol = NetworkOutputStream()
    __input_stream = NetworkInputStream()

    __mutex = threading.Lock()
    __log = ConsoleLog()

    __frame_data = bytes()

    def __init__(self, max_player):
        self.__timer = BattleSyncServer(self)
        self.__step_message = [[] for i in range(max_player)]
        self.__obj_pool = IndexObjectPool(max_player)

    def handle_msg(self, client_id, data):
        self.__mutex.acquire()
        self.__input_stream.reset_stream(data)
        self.__process_data(client_id, len(data))
        self.__mutex.release()

    def __process_data(self, client_id, length):
        if length < 4:
            self.__log.set_log("获取信息包大小失败\n")
            return

        if length < (self.__input_stream.get_len() + 4):
            self.__log.set_log("信息包大小不匹配\n")
            return

        if self.__input_stream.get_byte() == 3:
            cid = self.__input_stream.get_byte()
            self.__log.set_log("cid:" + str(cid) + "\n")
            self.__step_message[client_id] = self.__input_stream.get_last_bytes()
            self.__obj_pool.get(cid).set_active()

        count = length - self.__input_stream.get_len() - 4
        if count > 0:
            self.__process_data(client_id, count)

    def start_thead(self, cs, addr):
        battle_thread, client_id = self.__obj_pool.get_obj(BattleThread(cs, addr, self))
        battle_thread.set_client_id(client_id)
        battle_thread.start()

    def init_room(self, thread):
        self.__mutex.acquire()
        self.__protocol.push_char(1)
        self.__protocol.push_char(thread.get_client_id())
        self.__protocol.push_char(255)
        thread.send(self.__protocol.flush_stream())
        self.__timer.start()
        self.__mutex.release()

    def close_connect(self, client_id):
        if self.__mutex.acquire():
            try:
                self.__obj_pool.recover(client_id)
            finally:
                self.__mutex.release()

    def send_all_player(self):
        self.__mutex.acquire()
        if self.__obj_pool.get_active_count() <= 0:
            if len(self.__frame) > 0:
                self.__log.set_log("战斗结束\n")
                self.__timer.set_run(False)
                return

        if self.__frame == 0:
            self.__log.set_log("战斗开始\n")

        temp = self.__step_message
        length = len(temp)

        self.__protocol.push_char(3)
        self.__protocol.push_char(length)

        for i in range(length):
            self.__protocol.push_bool(len(temp[i]) > 0)
            self.__protocol.push_byte_array(temp[i])

        if len(self.__frame) == 0:
            self.__protocol.push_char(2)
            self.__protocol.push_integer(random.randint(0, 10000))

        self.__protocol.push_char(255)
        self.__log.set_log("生成帧信息[%d]\n" % length)

        self.__frame_data = self.__protocol.flush_stream()
        self.__frame.append(self.__frame_data)

        self.__obj_pool.foreach(self.send_to_client)
        self.__log.set_log("同步第[%d]\n" % len(self.__frame))

        self.__log.show_log()
        self.__mutex.release()

    def send_to_client(self, thread):
        if not thread.check_active():
            self.__log.set_log("客户端[%s] 断开了连接" % thread.get_addr())
            thread.close()
            self.__obj_pool.recover(thread.get_client_id)

        thread.send(self.__frame_data)


@unique
class BattleProtocolType(Enum):
    init = 1,
    random_seed = 2,
    frame = 3,
    end = 255

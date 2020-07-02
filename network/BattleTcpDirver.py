# coding=utf-8

import struct
from socket import *
import threading
import random
from time import sleep
from protocol.Command import InputCommand
from protocol.Command import SyncCommand
from protocol.Command import ConnectionCommand
from protocol.Command import CreateNewPlayerCommand
from core.Unit import Unit

from Log.ConsoleLog import ConsoleLog
from network.IndexObjectPool import IndexObjectPool
from network.NetworkInputStream import NetworkInputStream
from network.NetworkOutputStream import NetworkOutputStream

COMMAND_TYPE_INPUT = 0
COMMAND_TYPE_SYNC = 1
COMMAND_TYPE_CONNECT = 2
COMMAND_TYPE_DISCONNECT = 3


class BattleTcpServer(object):
    __socket = socket(AF_INET, SOCK_STREAM)
    __buf = 1024

    def __init__(self, ip, port):
        self.__address = (ip, port)
        self.__socket.bind(self.__address)
        self.__socket.listen(5)
        self.__msg_handler = ServiceGameLoop()
        self.__port = port
        self.__addr = ip

    def start_session(self):
        try:
            print "等待玩家"
            while True:
                cs, addr = self.__socket.accept()
                print addr
                self.__msg_handler.start_new_connect(cs, addr)

        except error as e:
            print e
            pass

    def get_bind_addr(self):
        return self.__addr, self.__port


class BattleThread(threading.Thread):
    __active = 30
    __buf = 1024

    __head_size = 4

    __client_id = -1

    __running = True

    def __init__(self, cs, addr, msg_handler):
        super(BattleThread, self).__init__()
        self.cs = cs
        self.addr = addr
        self.__msg_handler = msg_handler

    def set_client_id(self, client_id):
        self.__client_id = client_id

    def send(self, data):
        try:
            self.cs.sendall(data)
        except error as e:
            print e

    def run(self):
        try:
            while self.__running:
                data = self.cs.recv(self.__head_size)
                if not data:
                    break

                size = struct.unpack("i", data)[0]
                recv_data = b''
                recv_size = size
                print "recv size %d" % size
                while len(recv_data) < size:
                    recv_data = self.cs.recv(recv_size)
                    recv_size -= len(recv_data)

                self.__msg_handler.handle_msg(self, recv_data)

        except error as e:
            print e
            pass
        finally:
            self.__msg_handler.disconnected(self)
            self.cs.close()
            print "close cs"

    def close(self):
        self.__running = False

    def set_active(self):
        self.__active = 30

    def check_active(self):
        self.__active -= 1
        return self.__active >= 0

    def get_client_id(self):
        return self.__client_id


class BattleSyncServer(threading.Thread):

    def __init__(self, handler):
        super(BattleSyncServer, self).__init__()
        self.__handler = handler
        self.__running = True

    def run(self):
        while self.__running:
            self.__handler.update()
            sleep(0.02)

    def set_run(self, value):
        self.__running = value


class ServiceGameLoop(object):
    __buf = 1024
    __mutex = threading.Lock()

    __frame_count = 0
    __sync_list = []

    __sync_interval = 4

    __unit_dict = dict()
    __connect_dict = dict()

    __input = NetworkInputStream(None)

    def __init__(self):
        self.__game_loop_services = BattleSyncServer(self)
        self.__game_loop_services.start()

    def start_new_connect(self, cs, addr):
        if not self.__connect_dict.has_key(addr):
            connect = BattleThread(cs, addr, self)
            self.__connect_dict[addr] = connect
            connect.start()

    def update(self):
        self.__mutex.acquire()

        self.__frame_count += 1
        if self.__frame_count % self.__sync_interval == 0:
            sync = SyncCommand()
            sync.syncSnapshots = self.__sync_list
            self.send_to_all(sync)
            # print "send sync %d" % len(self.__sync_list)
            self.__sync_list = []

        frame_sync_list = []
        for unit in self.__unit_dict:
            frame = -1
            snapshot_list = self.__unit_dict[unit].snapshot_list
            while len(snapshot_list) > 0 and \
                    (self.__unit_dict[unit].count > self.__sync_interval or \
                     frame == -1 or snapshot_list[0].frame == frame):

                snapshot = snapshot_list[0]
                frame_sync_list.append(snapshot)
                self.__unit_dict[unit].snapshot_list.pop(0)
                snapshot_list = self.__unit_dict[unit].snapshot_list

                if frame != snapshot.frame:
                    frame = snapshot.frame
                    self.__unit_dict[unit].count -= 1

        if len(frame_sync_list) > 0:
            self.__sync_list.append(frame_sync_list)

        self.__mutex.release()

    def handle_msg(self, client, data):
        self.__mutex.acquire()

        self.__input.reset_stream(data, False)
        command_type = self.__input.get_integer()
        if command_type == COMMAND_TYPE_INPUT:
            if not self.__unit_dict.has_key(client.get_client_id()):
                self.__unit_dict[client.get_client_id()] = Unit()

            msg = InputCommand()
            msg.snapshots = self.__unit_dict[client.get_client_id()].snapshot_list
            msg.deserialize(self.__input)

            self.__unit_dict[client.get_client_id()].snapshot_list = msg.snapshots
            self.__unit_dict[client.get_client_id()].count += msg.snapshotFrameCount

            print "handler input msg"

        elif command_type == COMMAND_TYPE_CONNECT:
            print "Recv Connect Msg"
            msg = ConnectionCommand()
            msg.deserialize(self.__input)
            unit_id = msg.id

            if not self.__unit_dict.has_key(unit_id):
                self.__unit_dict[unit_id] = Unit()
                self.__unit_dict[unit_id].cs = client.cs
                client.set_client_id(unit_id)
                print "%d login success" % unit_id

                command = CreateNewPlayerCommand()
                command.id = unit_id
                command.hp = 100

                self.send_to_all(command)

            else:
                print "Account Already Login"

        self.__mutex.release()

    def send_to_one(self, unit_id, command):
        if self.__unit_dict.has_key(unit_id):
            self.__unit_dict[unit_id].cs.sendall(command.serialize())

    def send_to_all(self, command):
        for k in self.__unit_dict:
            pack = command.serialize()
            print "send size %d" % len(pack)
            self.__unit_dict[k].cs.sendall(pack)

    def disconnected(self, client):
        if client.addr in self.__connect_dict:
            del self.__connect_dict[client.addr]
        if client.get_client_id() in self.__unit_dict:
            del self.__unit_dict[client.get_client_id()]

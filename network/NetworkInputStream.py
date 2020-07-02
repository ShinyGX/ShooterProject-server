import struct

from protocol.Vector import Vector3
from protocol.Vector import Quaternion

class NetworkInputStream(object):
    __bytes = bytes()
    __index = 0
    __last_offset = 0
    __bytes_len = 0

    def reset_stream(self, b, has_head = True):
        self.__bytes = b[:]
        self.__index = 0
        self.__last_offset = 0
        if has_head:
            self.__seek(4)
            self.__bytes_len = struct.unpack("i", self.__bytes[0:4])[0]
        else:
            self.__bytes_len = len(b)

    def __init__(self, b):
        if b is None:
            self.__bytes_len = 0
            self.__bytes = None
        else:
            self.__bytes = b
            self.__bytes_len = len(b)
        self.__index = 0
        self.__last_offset = 0
       


    def get_len(self):
        return self.__bytes_len

    def get_integer(self):
        self.__seek(4)
        return struct.unpack("i", self.__get())[0]

    def get_char(self):
        self.__seek(1)
        return struct.unpack("c", self.__get())[0]

    def get_float(self):
        self.__seek(8)
        return struct.unpack("d",self.__get())[0]

    def get_vector3(self):
        x = self.get_float()
        y = self.get_float()
        z = self.get_float()
        v3 = Vector3()
        v3.x = x
        v3.y = y
        v3.z = z
        return v3

    def get_quaternion(self):
        x = self.get_float()
        y = self.get_float()
        z = self.get_float()
        w = self.get_float()
        q = Quaternion()
        q.x = x
        q.y = y
        q.z = z
        q.w = w
        return q

    def get_bool(self):
        self.__seek(4)
        return (struct.unpack("i",self.__get())[0] == 1)

    def get_byte(self):
        self.__seek(1)
        return struct.unpack("b", self.__get())[0]

    def get_data_bytes(self):
        if self.__bytes_len == 0:
            return None
        return self.__bytes[4:]

    def get_last_bytes(self):
        return self.__bytes[self.__index + self.__last_offset:]

    def get_data_len(self):
        return self.__bytes_len

    def __seek(self, offset):
        self.__index = self.__index + self.__last_offset
        self.__last_offset = offset

    def __get(self):
        if self.__last_offset + self.__index > self.__bytes_len:
            return None
        return self.__bytes[self.__index: self.__index + self.__last_offset]

import struct


class NetworkInputStream(object):
    __bytes = bytes()
    __index = 0
    __last_offset = 0
    __bytes_len = 0

    def reset_stream(self, b):
        self.__bytes = b
        self.__index = 0
        self.__last_offset = 0
        self.__seek(4)
        self.__bytes_len = struct.unpack("i", self.__bytes[0:4])[0]

    def get_len(self):
        return self.__bytes_len

    def get_integer(self):
        self.__seek(4)
        return struct.unpack("i", self.__get())[0]

    def get_char(self):
        self.__seek(1)
        return struct.unpack("c", self.__get())[0]

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

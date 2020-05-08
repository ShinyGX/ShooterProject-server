import struct


class NetworkOutputStream(object):
    __data = []

    def push_char(self, c):
        self.__data.append(struct.pack("c", chr(c)))

    def push_integer(self, i):
        self.__data.append(struct.pack("i", i))

    def push_string(self, s):
        st = s.encode("utf-8")
        t = str(len(st)) + "s"
        self.__data.append(struct.pack(t, st))

    def flush_stream(self):
        data = bytes()
        for i in range(len(self.__data)):
            t = str(len(self.__data[i])) + "s"
            data += struct.pack(t, self.__data[i])
        data_len = struct.pack("i", len(data))
        self.__data = []
        print "Output Data Size:", len(struct.unpack("i", data_len)), "Output Data TotalSize:", len(data + data_len)
        return data_len + data

    def __push_end_mask(self):
        self.push_char(255)
